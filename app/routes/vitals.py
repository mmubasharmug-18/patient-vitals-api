from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import SummaryOut, VitalsIn, VitalsOut
from app.storage import store
from app.summary import summarize

router = APIRouter(tags=["vitals"])


@router.post("/vitals", response_model=VitalsOut, status_code=201, summary="Record vitals for a patient")
def add_vitals(data: VitalsIn):
    return store.add(data)


@router.get("/patients/{patient_id}/vitals", response_model=list[VitalsOut], summary="List a patient's vitals, newest first")
def patient_vitals(
    patient_id: str,
    limit: Optional[int] = Query(None, ge=1, description="Return at most this many records (the newest ones)"),
):
    return store.for_patient(patient_id, limit)


@router.get("/patients/{patient_id}/summary", response_model=SummaryOut, summary="Average vitals and record count")
def patient_summary(patient_id: str):
    records = store.for_patient(patient_id)
    if not records:
        raise HTTPException(status_code=404, detail=f"No vitals found for patient {patient_id}")
    return summarize(patient_id, records)
