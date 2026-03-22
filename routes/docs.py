from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from schema.docShema import DocRecord, DocResponse, DocStatusResponse, DocType, DocStatus
from utils.pdfProcessing import PDFprocessor
from utils.docxProcessor import DocxProcessor
from utils.vec_store import Vector_store_service
from utils.s3 import S3Service
from db.connection import MongoDb
import tempfile, os, logging, asyncio
from datetime import datetime, timezone
from uuid import uuid4

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_TYPES = {
    "application/pdf": DocType.PDF,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocType.DOCX
}

async def process_and_embed(tmp_path: str, s3_key: str, file_type: DocType, org_id: str, doc_id: str):
    """
    Background task:
    1. Process temp file → chunks
    2. Add doc_id to chunk metadata
    3. Embed into ChromaDB
    4. Upload to S3
    5. Update MongoDB status
    6. Delete temp file
    """

    try: 
        await MongoDb.docs().update_one(
            {"doc_id": doc_id},
            {"$set": {"status": DocStatus.PROCESSING}}
        )

        if file_type == DocType.PDF:
            chunks = await asyncio.to_thread(PDFprocessor().processPDF, tmp_path)
        else:
            chunks = await asyncio.to_thread(DocxProcessor().process_docx, tmp_path)
        if not chunks:
            raise ValueError("No content extracted from document")
        
        for chunk in chunks:
            chunk.metadata["doc_id"] = doc_id

        vector_store = Vector_store_service(org_id=org_id)
        result = await asyncio.to_thread(
            vector_store.embed_documents, chunks
        )

        if result["status"] == "failed":
            raise RuntimeError(result.get("error", "embedding failed"))
        
        await asyncio.to_thread(S3Service.upload_file, tmp_path, s3_key)

        await MongoDb.docs().update_one(
            {"doc_id": doc_id},
            {"$set": {
                "status": DocStatus.COMPLETED,
                "chunk_count": result["embedded_count"],
                "completed_at": datetime.now(timezone.utc)
            }}
        )
        logger.info(f"[docs] Completed — org={org_id} doc={doc_id} chunks={result['embedded_count']}")

    except Exception as e:
        logger.error(f"[docs] Failed - doc => {doc_id}: {e}")
        await MongoDb.docs().update_one(
            {"doc_id": doc_id},
            {"$set": {
                "status": DocStatus.FAILED,
                "error": str(e)
            }}
        )
    finally:
        # always delete temp file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            logger.info(f"[docs] Temp file deleted — {tmp_path}")


@router.post("/upload", response_model=DocResponse)
async def upoad_document(
    background_tasks: BackgroundTasks,
    org_id: str = Form(...),
    file: UploadFile = File(...)
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Allowed: PDF, DOCX")
    
    org = await MongoDb.orgs().find_one({"org_id": org_id})
    
    if not org:
        raise HTTPException(status_code=404, detail=f"Org {org_id} not found")
    
    file_type = ALLOWED_TYPES[file.content_type]
    doc_id = str(uuid4())
    suffix = f".{file_type.value}"
    s3_key = f"docs/{org_id}/{doc_id}/{file.filename}"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while chunk := await file.read(1024*1024): #1mb chunks
                tmp.write(chunk)
            tmp_path = tmp.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    doc = DocRecord(
        doc_id=doc_id,
        org_id=org_id,
        filename=file.filename,
        file_type=file_type,
        s3_key = s3_key
    )

    await MongoDb.docs().insert_one(doc.model_dump(exclude_none=True))


    background_tasks.add_task(
        process_and_embed,
        tmp_path,
        s3_key,
        file_type, 
        org_id,
        doc_id
    )

    return DocResponse(
        doc_id=doc_id,
        filename=file.filename,
        s3_key=s3_key,
        status=DocStatus.PENDING,
        message="Document uploaded. Processing started."
    )

@router.get("/status/{org_id}/{doc_id}", response_model=DocStatusResponse)
async def get_document_status(org_id: str, doc_id: str):
    doc = await MongoDb.docs().find_one(
        {"doc_id": doc_id, "org_id": org_id},
        {"_id": 0}
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/{org_id}/{doc_id}/url")
async def get_document_url(org_id: str, doc_id: str):
    """Get the presigned url from s3 -- valid for 1 hour"""
    doc = await MongoDb.docs().find_one({"doc_id": doc_id, "org_id": org_id})
    if not doc:
        raise HTTPException(status_code=404, detail="document not found")
    url = await asyncio.to_thread(S3Service.get_url, doc["s3_key"])
    return {"url": url, "expires_in": 3600}


@router.delete("/delete/{org_id}/{doc_id}")
async def delete_document(org_id: str, doc_id: str):
    try:
        doc = await MongoDb.docs().find_one(
            {
                "doc_id": doc_id, 
                "org_id": org_id
            }
        )
        if not doc:
            raise HTTPException(status_code=404, detail = "Document not found")
        
        await asyncio.to_thread(S3Service.delete, doc["s3_key"])
        
        def delete_from_chroma():
            vector_store = Vector_store_service(org_id=org_id)
            collection = vector_store.get_collection()
            collection.delete(where={"doc_id": doc_id})
        
        await asyncio.to_thread(delete_from_chroma)
        
        await MongoDb.docs().delete_one({"doc_id": doc_id, "org_id": org_id})
        
        return {"message": f"Document {doc_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")
    
@router.get("/list_docs/{org_id}")
async def list_document(org_id: str):
    try:
        cursor = MongoDb.docs().find(
            {"org_id": org_id},
            {"_id": 0}
        ).sort("created_at", -1)
        docs = await cursor.to_list(length = 100)
        return {"org_id": org_id, "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")