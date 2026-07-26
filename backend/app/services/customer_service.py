from sqlalchemy.orm import Session

from backend.app.models.customer import Customer
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customer import CustomerCreate


class CustomerService:

    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate):

        customer = Customer(
            full_name=customer_data.full_name,
            phone=customer_data.phone,
            email=customer_data.email,
            address=customer_data.address
        )

        return CustomerRepository.create(db, customer)

    @staticmethod
    def get_customers(db: Session):
        return CustomerRepository.get_all(db)