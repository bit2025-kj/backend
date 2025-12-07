from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()

@router.post("/request_subscription", response_model=schemas.SubscriptionResponse)
def request_subscription(request: schemas.SubscriptionRequest, db: Session = Depends(get_db)):
    existing = crud.get_subscription_by_device(db, request.device_id)
    if existing:
        if existing.status == "pending":
            raise HTTPException(status_code=409, detail="Demande déjà en attente")
        if existing.status == "validated":
            raise HTTPException(status_code=409, detail="Device déjà activé")
    
    sub = crud.create_subscription(db, request.device_id, request.phone_number, request.months)
    return schemas.SubscriptionResponse(
        activation_key=sub.activation_key,
        status=sub.status,
        message="Clé générée, en attente de validation admin"
    )

@router.post("/check_subscription", response_model=schemas.SubscriptionCheckResponse)
def check_subscription(request: schemas.SubscriptionCheckRequest, db: Session = Depends(get_db)):
    sub = crud.get_subscription_by_device(db, request.device_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Device non trouvé")
    return schemas.SubscriptionCheckResponse(
        activation_key=sub.activation_key,
        expires_at=sub.expires_at.isoformat() if sub.expires_at else None,
        status=sub.status
    )

@router.post("/admin/validate/{device_id}")
def admin_validate(device_id: str, db: Session = Depends(get_db)):
    sub = crud.validate_subscription(db, device_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Device non trouvé ou déjà validé")
    return {"status": "validated", "expires_at": sub.expires_at.isoformat()}
