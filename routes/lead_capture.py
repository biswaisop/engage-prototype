from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from schema import leadResponse, leadForm

router = APIRouter()

@router.get("/")
async def create_lead(form: leadForm):
    pass