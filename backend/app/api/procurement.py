
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import String, Integer, Float, ForeignKey, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from ..database import Base, get_db
from ..main import User, get_current_user

router = APIRouter(tags=["Procurement"])


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    email: Mapped[str] = mapped_column(String(150), default="")
    category: Mapped[str] = mapped_column(String(100), default="General")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    status: Mapped[str] = mapped_column(String(30), default="Draft")
    total_amount: Mapped[float] = mapped_column(Float, default=0.0)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))


class SupplierCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: str = Field(default="", max_length=150)
    category: str = Field(default="General", max_length=100)


class SupplierResponse(BaseModel):
    id: int
    name: str
    email: str
    category: str


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    total_amount: float = Field(ge=0)


class PurchaseOrderResponse(BaseModel):
    id: int
    supplier_id: int
    status: str
    total_amount: float
    created_by: int


def supplier_out(s: Supplier) -> SupplierResponse:
    return SupplierResponse(
        id=s.id, name=s.name, email=s.email, category=s.category
    )


def order_out(o: PurchaseOrder) -> PurchaseOrderResponse:
    return PurchaseOrderResponse(
        id=o.id,
        supplier_id=o.supplier_id,
        status=o.status,
        total_amount=o.total_amount,
        created_by=o.created_by,
    )


def require_procurement_write(
    user: User = Depends(get_current_user),
) -> User:
    if user.role not in ("Owner", "Manager"):
        raise HTTPException(
            status_code=403,
            detail="Procurement write access required",
        )
    return user


@router.get("/suppliers", response_model=list[SupplierResponse])
def list_suppliers(
    search: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    statement = select(Supplier)

    if search:
        statement = statement.where(
            Supplier.name.ilike(f"%{search.strip()}%")
        )

    suppliers = db.scalars(
        statement.order_by(Supplier.id).limit(limit).offset(offset)
    ).all()
    return [supplier_out(s) for s in suppliers]


@router.post("/suppliers", response_model=SupplierResponse)
def create_supplier(
    request: SupplierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_procurement_write),
):
    supplier = Supplier(**request.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier_out(supplier)


@router.get("/purchase-orders", response_model=list[PurchaseOrderResponse])
def list_purchase_orders(
    order_status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    statement = select(PurchaseOrder)

    if order_status:
        statement = statement.where(PurchaseOrder.status == order_status)

    orders = db.scalars(
        statement.order_by(PurchaseOrder.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [order_out(o) for o in orders]


@router.post(
    "/purchase-orders",
    response_model=PurchaseOrderResponse,
)
def create_purchase_order(
    request: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_procurement_write),
):
    supplier = db.get(Supplier, request.supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    order = PurchaseOrder(
        supplier_id=request.supplier_id,
        total_amount=request.total_amount,
        status="Draft",
        created_by=user.id,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_out(order)


@router.post("/purchase-orders/{order_id}/submit")
def submit_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_procurement_write),
):
    order = db.get(PurchaseOrder, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    if order.status != "Draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft orders can be submitted",
        )

    order.status = "PendingApproval"
    db.commit()
    return {"message": "Purchase order submitted for approval", "id": order.id}


@router.post("/purchase-orders/{order_id}/approve")
def approve_purchase_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role != "Owner":
        raise HTTPException(status_code=403, detail="Owner approval required")

    order = db.get(PurchaseOrder, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    if order.status != "PendingApproval":
        raise HTTPException(
            status_code=400,
            detail="Only submitted orders can be approved",
        )

    order.status = "Approved"
    db.commit()
    return {"message": "Purchase order approved", "id": order.id}