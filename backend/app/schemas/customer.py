from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    full_name: str
    phone: str
    email: EmailStr
    address: str


class CustomerResponse(CustomerCreate):
    id: int
    status: str

    class Config:
        from_attributes = True