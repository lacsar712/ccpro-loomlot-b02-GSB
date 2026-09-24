from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models.fiber_catalog import FiberCatalog
from app.models.user import User
from app.schemas.fiber_catalog import FiberCatalogCreate, FiberCatalogUpdate, FiberCatalogOut

router = APIRouter(prefix="/api/fiber-catalog", tags=["fiber-catalog"])


@router.get("", response_model=List[FiberCatalogOut])
def list_fiber_catalog(
    enabled: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(FiberCatalog)
    if enabled is not None:
        q = q.filter(FiberCatalog.enabled == enabled)
    return q.order_by(FiberCatalog.id).all()


@router.post("", response_model=FiberCatalogOut, status_code=status.HTTP_201_CREATED)
def create_fiber_catalog(
    payload: FiberCatalogCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = FiberCatalog(
        fiber_name=payload.fiber_name,
        enabled=payload.enabled,
        max_capacity_l=payload.max_capacity_l,
    )
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="纤维名已存在")
    db.refresh(item)
    return item


@router.get("/{fiber_id}", response_model=FiberCatalogOut)
def get_fiber_catalog(
    fiber_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    item = db.query(FiberCatalog).filter(FiberCatalog.id == fiber_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="名录项不存在")
    return item


@router.put("/{fiber_id}", response_model=FiberCatalogOut)
def update_fiber_catalog(
    fiber_id: int,
    payload: FiberCatalogUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = db.query(FiberCatalog).filter(FiberCatalog.id == fiber_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="名录项不存在")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="纤维名已存在")
    db.refresh(item)
    return item


@router.delete("/{fiber_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fiber_catalog(
    fiber_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    item = db.query(FiberCatalog).filter(FiberCatalog.id == fiber_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="名录项不存在")
    db.delete(item)
    db.commit()
