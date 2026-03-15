from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from schema.docShema import DocRecord, DocResponse, DocStatusResponse, DocType, DocStatus
from utils.pdfProcessing import PDFprocessor
from utils.docxProcessor import DocxProcessor
from utils.vec_store import Vector_store_service