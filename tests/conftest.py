from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.v1.router import api_router  # noqa: F401
from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.main import app
from backend.app.database.database import Base
from backend.app.models.company import Company
from backend.app.models.customer import Customer
from backend.app.models.user import User  # noqa: F401
from backend.app.models.package import Package
from backend.app.models.subscription import Subscription
from backend.app.models.payment import Payment


@dataclass
class TestUser:
    """
    Minimal authenticated identity for API tests.

    API endpoints use company_id from the authenticated user
    to enforce tenant/company isolation.
    """

    company_id: int = 1
    is_active: bool = True


@pytest.fixture
def current_user() -> TestUser:
    return TestUser(company_id=1)


@pytest.fixture
def db_engine():
    """
    Create a disposable SQLite database for each test.

    The real development/production database is never used.
    """

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(
        dbapi_connection,
        connection_record,
    ):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(
        bind=engine,
        tables=[
            Company.__table__,
            Customer.__table__,
            Package.__table__,
            Subscription.__table__,
            Payment.__table__,
        ],
    )

    yield engine

    Base.metadata.drop_all(
        bind=engine,
        tables=[
            Payment.__table__,
            Subscription.__table__,
            Package.__table__,
            Customer.__table__,
            Company.__table__,
        ],
    )

    engine.dispose()


@pytest.fixture
def db(db_engine) -> Session:
    """
    Provide a clean database session and seed two tenants.
    """

    TestingSessionLocal = sessionmaker(
        bind=db_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    session = TestingSessionLocal()

    session.execute(
        Company.__table__.insert(),
        [
            {
                "id": 1,
                "name": "Orbit Test ISP One",
                "email": "isp1@test.orbitkonnect.local",
                "phone": "90000001",
                "country": "Oman",
                "currency": "OMR",
                "timezone": "Asia/Muscat",
                "subscription_plan": "FREE",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Orbit Test ISP Two",
                "email": "isp2@test.orbitkonnect.local",
                "phone": "90000002",
                "country": "Oman",
                "currency": "OMR",
                "timezone": "Asia/Muscat",
                "subscription_plan": "FREE",
                "is_active": True,
            },
        ],
    )

    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(
    db: Session,
    current_user: TestUser,
):
    """
    FastAPI TestClient with application dependencies overridden.

    Database access uses the disposable test database.
    Authentication uses a controlled authenticated test identity.
    """

    def override_get_db():
        yield db

    def override_get_current_user():
        return current_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def customer_payload():
    def _payload(**overrides):
        payload = {
            "full_name": "John Test Customer",
            "phone": "91234567",
            "email": "john.test@example.com",
            "address": "Muscat",
            "national_id": "TEST001",
        }

        payload.update(overrides)

        return payload

    return _payload


@pytest.fixture
def create_customer(db: Session):
    """
    Directly insert a customer for setup scenarios.

    This bypasses the API so tests can create precise database states
    without coupling setup to the behavior being tested.
    """

    def _create(company_id=1, **overrides):
        values = {
            "company_id": company_id,
            "full_name": "Existing Customer",
            "phone": "92222222",
            "email": "existing@example.com",
            "address": "Muscat",
            "national_id": "EXIST001",
            "is_active": True,
        }

        values.update(overrides)

        result = db.execute(
            Customer.__table__.insert().values(**values)
        )

        db.commit()

        customer_id = result.inserted_primary_key[0]

        return db.get(Customer, customer_id)

    return _create


@pytest.fixture
def create_package(db: Session):
    """
    Directly insert a package for setup scenarios.

    This bypasses the API so tests can create precise database states
    without coupling setup to the behavior being tested.
    """

    def _create(company_id=1, **overrides):
        values = {
            "company_id": company_id,
            "name": "Test Package",
            "download_speed_mbps": 15,
            "upload_speed_mbps": 10,
            "duration_value": 30,
            "duration_unit": "DAY",
            "price": 6,
            "description": "Test package",
            "is_active": True,
        }

        values.update(overrides)

        result = db.execute(
            Package.__table__.insert().values(**values)
        )

        db.commit()

        package_id = result.inserted_primary_key[0]

        return db.get(Package, package_id)

    return _create