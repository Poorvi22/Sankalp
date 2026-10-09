
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import String, Float, Integer, select, or_
from sqlalchemy.orm import Mapped, Session, mapped_column

from ..database import Base, get_db
from ..main import get_current_user, User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150), index=True)
    category: Mapped[str] = mapped_column(String(80), default="General")
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    reorder_level: Mapped[int] = mapped_column(Integer, default=10)
    unit_price: Mapped[float] = mapped_column(Float, default=0.0)


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    category: str = Field(default="General", max_length=80)
    quantity: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)
    unit_price: float = Field(default=0.0, ge=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    category: str | None = Field(default=None, max_length=80)
    quantity: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)
    unit_price: float | None = Field(default=None, ge=0)


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    category: str
    quantity: int
    reorder_level: int
    unit_price: float


def as_product(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        category=product.category,
        quantity=product.quantity,
        reorder_level=product.reorder_level,
        unit_price=product.unit_price,
    )


def require_inventory_write(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("Owner", "Warehouse"):
        raise HTTPException(status_code=403, detail="Inventory write access required")
    return user


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    search: str | None = None,
    low_stock: bool = False,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    statement = select(Product)

    if search:
        term = f"%{search.strip()}%"
        statement = statement.where(
            or_(Product.name.ilike(term), Product.sku.ilike(term))
        )

    if low_stock:
        statement = statement.where(Product.quantity <= Product.reorder_level)

    products = db.scalars(
        statement.order_by(Product.id).limit(limit).offset(offset)
    ).all()

    return [as_product(product) for product in products]


@router.post("/products", response_model=ProductResponse)
def create_product(
    request: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_inventory_write),
):
    existing = db.scalar(select(Product).where(Product.sku == request.sku))
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")

    product = Product(**request.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return as_product(product)


@router.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    request: ProductUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_inventory_write),
):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return as_product(product)


@router.get("/summary")
def inventory_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    total_products = db.query(Product).count()
    low_stock_count = db.query(Product).filter(
        Product.quantity <= Product.reorder_level
    ).count()

    return {
        "total_products": total_products,
        "low_stock_products": low_stock_count,
    }