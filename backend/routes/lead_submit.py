import re
from fastapi import APIRouter, HTTPException
from schema.leadSchema import leadDocument, leadExtraction, leadForm, leadResponse, LeadSource, LeadStatus
from db.connection import MongoDb
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/submit_leads", response_model=leadResponse)
async def submit_lead_form(form: leadForm):
    
    doc = leadDocument(
        thread_id=form.thread_id,
        org_id=form.org_id,
        name=form.name,
        email=form.email,
        phone=form.phone,
        check_in=form.check_in,
        check_out=form.check_out,
        room_type=form.room_type,
        guest_count=form.guest_count,
        notes=form.notes,
        source=LeadSource.CHAT,
        status=LeadStatus.NEW,
    )
    
    result = await MongoDb.leads().insert_one(doc.model_dump())
    if not result.inserted_id:
        raise HTTPException(status_code=500, deatil = "Failed to save data")

    return leadResponse(
        thread_id=form.thread_id,
        message="Thanks! We've received your booking request and will confirm shortly.",
    )
    
    
