from pydantic import BaseModel


class Product(BaseModel):
    product_id: int = None
    name: str
    unit_price: float
    description: str
    img_url: str
