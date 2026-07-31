from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.dependencies.database import get_db
from backend.app.models.package import Package
from backend.app.schemas.package import PackageCreate

router = APIRouter(
    prefix="/packages",
    tags=["Packages"]
)


@router.post("/")
def create_package(package: PackageCreate, db: Session = Depends(get_db)):

    new_package = Package(
        name=package.name,
        speed=package.speed,
        duration=package.duration,
        price=package.price,
        description=package.description
    )

    db.add(new_package)
    db.commit()
    db.refresh(new_package)

    return new_package


@router.get("/")
def get_packages(db: Session = Depends(get_db)):
    return db.query(Package).all()


@router.get("/{package_id}")
def get_package(package_id: int, db: Session = Depends(get_db)):

    package = db.query(Package).filter(
        Package.id == package_id
    ).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    return package


@router.put("/{package_id}")
def update_package(
    package_id: int,
    updated: PackageCreate,
    db: Session = Depends(get_db)
):

    package = db.query(Package).filter(
        Package.id == package_id
    ).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    package.name = updated.name
    package.speed = updated.speed
    package.duration = updated.duration
    package.price = updated.price
    package.description = updated.description

    db.commit()
    db.refresh(package)

    return package


@router.delete("/{package_id}")
def delete_package(package_id: int, db: Session = Depends(get_db)):

    package = db.query(Package).filter(
        Package.id == package_id
    ).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    db.delete(package)
    db.commit()

    return {"message": "Package deleted successfully"}