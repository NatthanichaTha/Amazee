from datetime import datetime

from pydantic import BaseModel

from schemas.product import Product
from schemas.user import PaymentInfo, ShippingInfo


class OrderProducts(BaseModel):
    product_id: int
    quantity: int


class Order(BaseModel):
    order_id: int = None
    timestamp: datetime = datetime.now()
    user_id: int
    payment_id: int
    address_id: int
    order_status: str = "Pending"
    products: list[OrderProducts]
