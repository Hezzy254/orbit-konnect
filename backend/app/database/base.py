from backend.app.database.database import Base

# Import all models here so Alembic can detect them
from backend.app.models.company import Company
from backend.app.models.customer import Customer
from backend.app.models.package import Package
from backend.app.models.user import User