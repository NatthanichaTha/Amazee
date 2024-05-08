from fastapi import APIRouter, Response

from schemas.generic import ResponseMsg
from schemas.product import Product
import sqlite3

router = APIRouter(prefix="/product")
con = sqlite3.connect("amazee.db")


@router.put("/product")
async def add_product(product: Product, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            """
                    INSERT INTO products(name, unit_price, description, img_url)
                    VALUES(?,?,?,?)
                    """,
            [product.name, product.unit_price, product.description, product.img_url],
        )
        con.commit()
    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="Product added")


@router.post("/product")
async def modify_product(product: Product, response: Response) -> ResponseMsg:
    try:
        cur = con.cursor()
        cur.execute(
            """
                    UPDATE products
                    SET name = ?, 
                    unit_price = ?,
                    description = ?, 
                    img_url = ?
                    WHERE product_id = ?
            """,
            [
                product.name,
                product.unit_price,
                product.description,
                product.img_url,
                product.product_id,
            ],
        )
        con.commit()
    except sqlite3.IntegrityError as e:
        response.status_code = 400
        return ResponseMsg(msg=f"Error occurred: {str(e)}")

    return ResponseMsg(msg="Product info modified")


@router.delete("/product/{product_id}")
async def delete_product(product_id: int, response: Response) -> ResponseMsg:
    cur = con.cursor()
    cur.execute(
        "DELETE FROM products WHERE product_id = ?",
        (product_id),
    )
    con.commit()
    if cur.rowcount == 0:
        response.status_code = 404
        return ResponseMsg(msg="Product id not found")

    return ResponseMsg(msg="Product deleted")


@router.get("/search")
async def search_product(search_query: str, response: Response) -> list[Product]:
    try:
        cur = con.cursor()
        cur.execute(
            """ 
            SELECT * FROM products
            WHERE name LIKE ? OR name LIKE '%' || ? || '%' OR description LIKE '%' || ? || '%'
            """,
            (search_query, search_query, search_query),
        )
        res = cur.fetchall()
        product_infos = []
        for row in res:
            product = Product(
                product_id=row[0],
                name=row[1],
                unit_price=row[2],
                description=row[3],
                img_url=row[4],
            )
            product_infos.append(product)
        return product_infos

    except Exception as e:
        response.status_code = 500
        return ResponseMsg(msg=f"Error occurred: {str(e)}")
