from fastapi import APIRouter, Response

from schemas.generic import ResponseMsg
from schemas.order import Order

import sqlite3

router = APIRouter(prefix="/order")
con = sqlite3.connect("amazee.db")


@router.put("/order")
async def place_order(order: Order, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            "INSERT INTO orders(timestamp, user_id, payment_id, address_id, order_status) VALUES (?,?,?,?,?)",
            [
                order.timestamp,
                order.user_id,
                order.payment_id,
                order.address_id,
                order.order_status,
            ],
        )
        # get order_id
        order_id = cur.lastrowid

        for item in order.products:
            cur.execute(
                "INSERT INTO order_products(order_id, product_id, quantity) VALUES (?,?,?)",
                (order_id, item.product_id, item.quantity),
            )

        con.commit()

    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="order success")


@router.get("/order/{user_id}")
async def get_order(user_id: int, response: Response) -> list[dict]:
    cur = con.cursor()
    cur.execute(
        """
        SELECT orders.order_id, orders.timestamp, orders.user_id, user_payment_info.card_no, orders.order_status, 
        user_shipping_info.zip_code, user_shipping_info.country, user_shipping_info.city, user_shipping_info.street  
        FROM orders 
        JOIN user_shipping_info ON orders.address_id = user_shipping_info.address_id
        JOIN user_payment_info ON orders.payment_id = user_payment_info.payment_id
        WHERE orders.user_id = ?""",
        [user_id],
    )
    res = cur.fetchall()
    order_list = []
    for row in res:
        order = {}
        order["order_id"] = row[0]
        order["timestamp"] = row[1]
        order["user_id"] = row[2]
        order["payment(card_no.)"] = row[3]
        order["order_status"] = row[4]
        order["shipping_address"] = " ".join(row[5:])

        order["products"] = []
        # find all products in each orders
        cur.execute(
            """SELECT order_products.product_id, products.name, products.unit_price, products.img_url, quantity 
            FROM order_products 
            JOIN products ON order_products.product_id = products.product_id WHERE order_products.order_id = ?""",
            [order["order_id"]],
        )
        product_res = cur.fetchall()

        for item in product_res:
            product = {}
            product["product_id"] = item[0]
            product["product_name"] = item[1]
            product["unit_price"] = item[2]
            product["img_url"] = item[3]
            product["quantity"] = item[4]
            order["products"].append(product)

        order_list.append(order)

    return order_list
