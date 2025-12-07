from pydantic import BaseModel

class SubscriptionRequest(BaseModel):
    device_id: str
    phone_number: str
    months: int

class SubscriptionResponse(BaseModel):
    activation_key: str
    status: str
    message: str | None = None

class SubscriptionCheckRequest(BaseModel):
    device_id: str

class SubscriptionCheckResponse(BaseModel):
    activation_key: str
    expires_at: str | None = None
    status: str
