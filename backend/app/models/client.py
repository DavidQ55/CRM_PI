from pydantic import BaseModel, EmailStr

class Client(BaseModel):
    name: str
    email: EmailStr
    phone: str
    segment: str = "General"