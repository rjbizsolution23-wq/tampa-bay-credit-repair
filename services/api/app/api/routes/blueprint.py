from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.core.database import get_db
from app.services.audit.blueprint_service import blueprint_service
from app.services.pdf_generator import pdf_generator
from app.models.audit import BlueprintAudit, AuditItem, AuditRecommendation, ConsultationForm, AuditStatus
# from app.models.credit_report import CreditReport # Needed if we query it directly
# from app.models.user import User

router = APIRouter()

@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_audit(
    payload: Dict[str, Any], 
    db: Session = Depends(get_db)
):
    """
    Start a new blueprint audit for a credit report.
    Payload: { "creditReportId": "...", "userId": "..." }
    """
    credit_report_id = payload.get("creditReportId")
    user_id = payload.get("userId")
    
    if not credit_report_id or not user_id:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Fetch Credit Report (Mocking the fetch for now as models aren't fully set up for CreditReport)
    # In a real scenario: cr = db.query(CreditReport).get(credit_report_id)
    # We will assume we can get the RAW JSON or pass the object to the service.
    # For this implementation, let's assume we can query it or we'll pass a mock object if DB is empty.
    
    # TODO: Fetch actual CR data. 
    # For now, we'll create the Audit record directly.
    
    # Run Analysis (This normally needs the loaded CreditReport object with tradelines)
    # analysis = await blueprint_service.run_audit(credit_report_obj)
    
    # Create Audit Record
    audit_id = str(uuid.uuid4())
    audit = BlueprintAudit(
        id=audit_id,
        userId=user_id,
        creditReportId=credit_report_id,
        status=AuditStatus.PENDING_REVIEW,
        # Fill with analysis results...
        totalViolationsFound=0, # Placeholder until CR fetch is real
        createdAt=datetime.now(),
        updatedAt=datetime.now()
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    
    return {"id": audit.id, "status": audit.status}

@router.get("/{audit_id}")
def get_audit(audit_id: str, db: Session = Depends(get_db)):
    audit = db.query(BlueprintAudit).filter(BlueprintAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
        
    # Eager load items if needed, or rely on lazy loading
    return audit

@router.post("/{audit_id}/complete")
async def complete_audit(
    audit_id: str, 
    data: Dict[str, Any], 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    audit = db.query(BlueprintAudit).filter(BlueprintAudit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
        
    # Save Consultation Form
    form_data = data.get("consultation", {})
    form = ConsultationForm(
        id=str(uuid.uuid4()),
        auditId=audit_id,
        clientFirstName=form_data.get("firstName"),
        clientLastName=form_data.get("lastName"),
        # ... other fields
    )
    db.add(form)
    
    # Update Status
    audit.status = AuditStatus.COMPLETED
    db.commit()
    
    # Generate PDF in background
    background_tasks.add_task(generate_and_save_pdf, audit_id, db)
    
    return {"status": "completed", "auditId": audit_id}

# Helper
def generate_and_save_pdf(audit_id: str, db: Session):
    # dedicated session or pass ID
    pass
    # Logic: fetch full audit data -> pdf_generator.generate -> upload to R2 -> update audit.clientBlueprintUrl
