from langchain_core.documents import Document
from typing import List
import chromadb
from chromadb.utils import embedding_functions
import uuid
from dotenv import load_dotenv
import os



load_dotenv()

class Vector_store_service:
    
    _embedding_model = None
    _chromadb_client = None
    
    @classmethod
    def get_chromadb_client(cls):
        if cls._chromadb_client is None:
            chroma_api_key = os.getenv("CHROMADB_API_KEY")
            chroma_tenant = os.getenv("CHROMADB_TENANT")
            database = os.getenv("VECTOR_DB")
            cls._chromadb_client = chromadb.CloudClient(
                tenant=chroma_tenant,
                api_key=chroma_api_key,
                database=database
            )
        return cls._chromadb_client
    
    @classmethod
    def get_embedding_model(cls):
        if cls._embedding_model is None:
            cls._embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
                                    model_name=os.getenv("EMBEDDING_MODEL")
            )
        return cls._embedding_model
    
    def __init__(self, org_id):
        self.collection = org_id
        self.embedding_model =  self.get_embedding_model()
        self.client = self.get_chromadb_client()
        

    def get_collection(self):
        try:
            return self.client.get_or_create_collection(
                name = f"kb_{self.collection}",
                embedding_function = self.embedding_model
            )
        except Exception as e:
            raise RuntimeError (
                f"failed to initialize for org {self.collection}: {str(e)}"
            )
    def embed_documents(self, chunks:List[Document], batch_size:int = 100, doc_id:str = None):
        if not chunks:
            raise ValueError("No documents provided for embedding")
        collection = self.get_collection()

        ids = []
        texts = []
        metadata = []

        for chunk in chunks:
            ids.append(str(uuid.uuid4()))
            texts.append(chunk.page_content)
            # metadata.append(chunk.metadata or {})
            meta = chunk.metadata or {}
            if doc_id:
                meta["doc_id"] = doc_id
            metadata.append(meta)

        total = len(ids)
        embedded_count = 0
        
        try:
            for i in range(0, total, batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_texts = texts[i:i+batch_size]
                batch_metadata = metadata[i:i+batch_size]
                try:
                    collection.add(
                        ids=batch_ids,
                        documents=batch_texts,
                        metadatas=batch_metadata
                    )
                    embedded_count += len(batch_ids)
                except ValueError as ve:
                    raise ValueError(
                        f"Batch insertion failed at index {i}:{str(ve)}"
                    )
                except Exception as batch_error:
                    raise RuntimeError(
                        f"Unexpected error during batch insertion at index {i}: {str(batch_error)}"
                    )
            return {
                "status":"success",
                "embedded_count": embedded_count
            }
        except Exception as e:
            return {
                "status":"failed",
                "embedded_count": embedded_count,
                "error":str(e)
            }


    def retrieve_documents(self, query:str, k:int = 5, thresold:float = 0.7):
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        try:
            collection = self.get_collection()

            results = collection.query(
                query_texts=[query],
                n_results=k
            )

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ids = results.get("ids", [[]])[0]

            filtered_docs = []

            for doc, meta, dist, doc_id in zip(documents, metadatas, distances, ids):
                if dist <= thresold:
                    filtered_docs.append({
                        "id":doc_id,
                        "content":doc, 
                        "metadata":meta,
                        "distance":dist,
                    })

            return {
                "status":"success",
                "query": query,
                "total_retrieved": len(documents),
                "filtered_count": len(filtered_docs),
                "results": filtered_docs
            }
        except ValueError as ve:
            return {
            "status": "failed",
            "error_type": "validation_error",
            "error": str(ve)
            }
        except Exception as e:
        # Cloud/network/Chroma failure
            return {
                "status": "failed",
                "error_type": "retrieval_error",
                "error": str(e)
            }

if __name__ == "__main__":
    vector = Vector_store_service("test-org-1")
    collection = vector.get_collection()
    results = vector.retrieve_documents("learner autonomy defined according to Holec")
    print(results)