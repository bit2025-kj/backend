from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import crud
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="_ap_bar Backend - Client")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SubscriptionRequest(BaseModel):
    device_id: str
    phone_number: str
    months: int

class CheckSubscriptionRequest(BaseModel):  # ✅ AJOUTÉ pour Flutter
    device_id: str

@app.post("/request_subscription")
async def request_subscription(request: SubscriptionRequest, db: Session = Depends(get_db)):
    existing = crud.get_subscription_by_device(db, request.device_id)
    if existing and existing.status == "pending":
        return {"activation_key": existing.activation_key, "status": "pending"}
    
    sub = crud.create_subscription(db, request.device_id, request.phone_number, request.months)
    print(f"🆕 NOUVELLE DEMANDE: {request.device_id} | Clé: {sub.activation_key}")
    return {"activation_key": sub.activation_key, "status": "pending"}

# ✅ CORRIGÉ POUR FLUTTER (fix 422)
@app.post("/check_subscription")
async def check_subscription(request: CheckSubscriptionRequest, db: Session = Depends(get_db)):
    print(f"🔍 Flutter check pour: {request.device_id}")  # DEBUG
    sub = crud.get_subscription_by_device(db, request.device_id)
    if not sub:
        print(f"❌ Device {request.device_id} non trouvé")
        return {"error": "Device non trouvé"}
    print(f"📊 Status actuel: {sub.status}")  # DEBUG
    return {
        "activation_key": sub.activation_key,
        "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
        "status": sub.status
    }

@app.post("/admin/validate/{device_id}")
async def admin_validate(device_id: str, db: Session = Depends(get_db)):
    print(f"[DEBUG] Validation admin pour: {device_id}")
    success = crud.validate_subscription(db, device_id)
    if success:
        print(f"✅ VALIDÉ: {device_id}")
        return {"status": "validated"}
    print(f"[WARN] Échec validation: {device_id}")
    return {"error": "Device non trouvé ou déjà validé"}

@app.get("/admin/pending")
async def get_pending(db: Session = Depends(get_db)):
    pending = crud.get_pending_requests(db)
    return [{"device_id": p.device_id, "phone": p.phone_number, "key": p.activation_key, "months": p.months} for p in pending]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
