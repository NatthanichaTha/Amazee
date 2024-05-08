from pydantic import BaseModel


class Nums(BaseModel):
    asd: str
    nums: list[int]


class UserInfo(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    password: str


class Credentials(BaseModel):
    email: str
    password: str


class ShippingInfo(BaseModel):
    address_id: int = None
    user_id: int
    zip_code: str
    country: str
    city: str
    street: str


class PaymentInfo(BaseModel):
    payment_id: int = None
    user_id: int
    card_no: str
    holder_name: str
    exp: str
