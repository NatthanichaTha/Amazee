from fastapi import APIRouter, Response

from schemas.generic import ResponseMsg
from schemas.user import Credentials, PaymentInfo, ShippingInfo, UserInfo
import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def is_user_email(email):
    cur = con.cursor()
    cur.execute("SELECT user_id from users WHERE email = ?", [email])
    res = cur.fetchone()
    if res is None:
        return False
    return True


router = APIRouter(prefix="/users")
con = sqlite3.connect("amazee.db")


@router.post("/register")
async def register_user(info: UserInfo, response: Response) -> ResponseMsg:
    hashed_password = get_password_hash(info.password)
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users(username, email, hashed_password, first_name, last_name) VALUES (?,?,?,?,?)",
            [
                info.username,
                info.email,
                hashed_password,
                info.first_name,
                info.last_name,
            ],
        )
        con.commit()
    except:
        response.status_code = 400
        return ResponseMsg(msg="username or email already exists")
    return ResponseMsg(msg="register completed")


@router.get("/login")
async def login(credentials: Credentials, response: Response) -> ResponseMsg:

    if is_user_email(credentials.email) == False:
        response.status_code = 400
        return ResponseMsg(msg="email does not exists")

    cur = con.cursor()
    cur.execute(
        "SELECT hashed_password FROM users WHERE email = ?", [credentials.email]
    )
    hashed_password = cur.fetchone()[0]

    if verify_password(credentials.password, hashed_password) == False:
        response.status_code = 400
        return ResponseMsg(msg="incorrect password")
    elif verify_password(credentials.password, hashed_password) == True:
        return ResponseMsg(msg="Password matched")


@router.put("/address")
async def add_address(info: ShippingInfo, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_shipping_info(user_id, country, zip_code, city, street) VALUES (?,?,?,?,?)",
            (info.user_id, info.country, info.zip_code, info.city, info.street),
        )
        con.commit()

    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="Address added")


@router.post("/address")
async def modify_address(info: ShippingInfo, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            """
                    UPDATE user_shipping_info 
                    SET country = ?, 
                    zip_code = ?,
                    city = ?, 
                    street = ?
                    WHERE address_id = ?
            """,
            [info.country, info.zip_code, info.city, info.street, info.address_id],
        )
        con.commit()
    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="Address modified")


@router.delete("/address/{address_id}")
async def delete_address(address_id: int, response: Response) -> ResponseMsg:
    cur = con.cursor()
    cur.execute(
        "DELETE FROM user_shipping_info WHERE address_id = ?",
        (address_id),
    )
    con.commit()
    if cur.rowcount == 0:
        response.status_code = 404
        return ResponseMsg(msg="Address id not found")

    return ResponseMsg(msg="Address deleted")


@router.get("/address/{user_id}")
async def get_address(user_id: int, response: Response) -> list[ShippingInfo]:
    cur = con.cursor()
    cur.execute("SELECT * FROM user_shipping_info WHERE user_id = ?", [user_id])
    res = cur.fetchall()
    shipping_infos = []
    for row in res:
        shipping_info = ShippingInfo(
            address_id=row[0],
            user_id=row[1],
            country=row[2],
            zip_code=row[3],
            city=row[4],
            street=row[5],
        )
        shipping_infos.append(shipping_info)

    return shipping_infos


@router.put("/payment_method")
async def add_payment_method(info: PaymentInfo, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO user_payment_info(payment_id, user_id, card_no, holder_name, exp) VALUES (?,?,?,?,?)",
            (info.payment_id, info.user_id, info.card_no, info.holder_name, info.exp),
        )
        con.commit()

    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="Payment method added")


@router.post("/payment_method")
async def modify_payment_method(info: PaymentInfo, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            """
                    UPDATE user_payment_info 
                    SET card_no = ?, 
                    holder_name = ?,
                    exp = ?, 
                    WHERE payment_id = ?
            """,
            [info.card_no, info.holder_name, info.exp, info.payment_id],
        )
        con.commit()
    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="Address modified")


@router.delete("/payment_method/{payment_id}")
async def delete_payment_method(payment_id: int, response: Response) -> ResponseMsg:
    cur = con.cursor()
    cur.execute(
        "DELETE FROM user_payment_info WHERE payment_id = ?",
        (payment_id),
    )
    con.commit()
    if cur.rowcount == 0:
        response.status_code = 404
        return ResponseMsg(msg="Payment id not found")

    return ResponseMsg(msg="Payment info deleted")


@router.get("/payment_method/{user_id}")
async def get_payment_method(user_id: int, response: Response) -> list[PaymentInfo]:
    cur = con.cursor()
    cur.execute("SELECT * FROM user_payment_info WHERE user_id = ?", [user_id])
    res = cur.fetchall()
    payment_infos = []
    for row in res:
        payment_info = PaymentInfo(
            payment_id=row[0],
            user_id=row[1],
            card_no=row[2],
            holder_name=row[3],
            exp=row[4],
        )
        payment_infos.append(payment_info)

    return payment_infos
