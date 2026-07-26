from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.schemas.customer import CustomerCreate
from backend.app.services.customer_service import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.post("/")
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    return CustomerService.create_customer(db, customer)


@router.get("/")
def get_customers(
    db: Session = Depends(get_db)
):
    return CustomerService.get_customers(db)