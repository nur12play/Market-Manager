import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Market-Manager")
DB = "market.db"


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0
            )
        """)


init_db()


class ProductIn(BaseModel):
    barcode: str
    name: str
    price: float
    stock: int = 0


@app.post("/products")
def add_product(p: ProductIn):
    try:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO products (barcode, name, price, stock) VALUES (?, ?, ?, ?)",
                (p.barcode, p.name, p.price, p.stock),
            )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Товар с таким штрихкодом уже есть")
    return {"message": "Товар добавлен"}


@app.get("/products")
def list_products():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM products").fetchall()
    return [dict(r) for r in rows]


@app.get("/products/{barcode}")
def get_product(barcode: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE barcode = ?", (barcode,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return dict(row)