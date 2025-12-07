from sqlalchemy.orm import Session
from models import Subscription
from datetime import datetime, timedelta
import random
import string

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def create_subscription(db: Session, device_id: str, phone: str, months: int):
    key = generate_key()
    sub = Subscription(device_id=device_id, phone_number=phone, months=months, activation_key=key)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

def get_subscription_by_device(db: Session, device_id: str):
    return db.query(Subscription).filter(Subscription.device_id == device_id).first()

def validate_subscription(db: Session, device_id: str):
    sub = get_subscription_by_device(db, device_id)
    if sub and sub.status == "pending":
        sub.status = "validated"
        sub.expires_at = datetime.utcnow() + timedelta(days=sub.months*30)
        db.commit()
        return True
    return False

def get_pending_requests(db: Session):
    return db.query(Subscription).filter(Subscription.status == "pending").all()
