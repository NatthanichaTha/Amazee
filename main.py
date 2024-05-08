import uvicorn
from fastapi import FastAPI

from routes.user import router as user_router
from routes.product import router as product_router
from routes.order import router as order_router

import sqlite3

from fastapi import Depends, FastAPI


app = FastAPI()
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)

con = sqlite3.connect("amazee.db")


def init_db():
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            hashed_password TEXT,
            first_name TEXT,
            last_name TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_shipping_info(
            address_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            country TEXT,
            zip_code TEXT,
            city TEXT,
            street TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS user_payment_info(
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            card_no TEXT,
            holder_name TEXT,
            exp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products(
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            unit_price FLOAT,
            description TEXT,
            img_url TEXT
        )
        """
    )
    # cur.execute("DROP TABLE orders")  ###delete table

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders(
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        payment_id INTEGER,
        address_id INTEGER,
        order_status TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (payment_id) REFERENCES user_payment_info(payment_id),
        FOREIGN KEY (address_id) REFERENCES user_shipping_info(address_id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS order_products(
            order_id INTEGER,
            product_id INTEGER, 
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            PRIMARY KEY (order_id, product_id)
        )
        """
    )
    con.commit()


@app.on_event("startup")
def on_startup():
    init_db()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
