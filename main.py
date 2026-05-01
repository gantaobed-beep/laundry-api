from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import sqlite3
import json
from uuid import uuid4
from datetime import datetime, timezone

app = FastAPI(title="Laundry Order Management System")

# --- Database Setup (SQLite) ---
def init_db():
    conn = sqlite3.connect("laundry.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT,
            phone TEXT,
            garments TEXT,
            total_amount REAL,
            status TEXT,
            created_at TEXT
        )
    ''')
    
    # Seed initial demo data if table is empty
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        sample_g1 = json.dumps([{"type": "Saree", "quantity": 1, "price": 200, "total": 200}])
        sample_g2 = json.dumps([{"type": "Pants", "quantity": 2, "price": 80, "total": 160}])
        cursor.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (str(uuid4()), "Meghana", "9876543210", sample_g1, 200.0, "RECEIVED", datetime.now(timezone.utc).isoformat()))
        cursor.execute("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (str(uuid4()), "Prakash", "5551234567", sample_g2, 160.0, "PROCESSING", datetime.now(timezone.utc).isoformat()))
    
    conn.commit()
    conn.close()

init_db()

# --- Configuration ---
PRICES = {"Shirt": 50, "Pants": 80, "Saree": 200, "Jacket": 150}
VALID_STATUSES = ['RECEIVED', 'PROCESSING', 'READY', 'DELIVERED']

# --- Input Models ---
class GarmentInput(BaseModel):
    type: str = Field(..., description="E.g., Shirt, Pants, Saree")
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    customerName: str
    phone: str
    garments: List[GarmentInput]

class StatusUpdate(BaseModel):
    status: str

# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("index.html", "r") as f:
        return f.read()

@app.post("/api/orders", status_code=201)
def create_order(order: OrderCreate):
    if not order.garments:
        raise HTTPException(status_code=400, detail="Order must contain garments.")

    total_amount = 0
    processed_garments = []

    for g in order.garments:
        price = PRICES.get(g.type, 0)
        item_total = price * g.quantity
        total_amount += item_total
        processed_garments.append({"type": g.type, "quantity": g.quantity, "price": price, "total": item_total})

    order_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect("laundry.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (id, customer_name, phone, garments, total_amount, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (order_id, order.customerName, order.phone, json.dumps(processed_garments), total_amount, "RECEIVED", created_at)
    )
    conn.commit()
    conn.close()

    return {"message": "Order created", "orderId": order_id, "totalAmount": total_amount}

@app.get("/api/orders")
def get_orders(
    status: Optional[str] = None, 
    customerName: Optional[str] = None, 
    phone: Optional[str] = None
):
    conn = sqlite3.connect("laundry.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM orders WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status.upper())
    if customerName:
        query += " AND LOWER(customer_name) LIKE ?"
        params.append(f"%{customerName.lower()}%")
    if phone:
        query += " AND phone LIKE ?"
        params.append(f"%{phone}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.patch("/api/orders/{order_id}/status")
def update_status(order_id: str, update: StatusUpdate):
    if update.status.upper() not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")

    conn = sqlite3.connect("laundry.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (update.status.upper(), order_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    conn.commit()
    conn.close()
    return {"message": "Status updated successfully"}

@app.get("/api/dashboard")
def get_dashboard():
    conn = sqlite3.connect("laundry.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(total_amount) FROM orders")
    total_orders, total_revenue = cursor.fetchone()
    
    cursor.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
    status_counts = {status: 0 for status in VALID_STATUSES}
    for row in cursor.fetchall():
        status_counts[row[0]] = row[1]
        
    conn.close()

    return {
        "totalOrders": total_orders or 0,
        "totalRevenue": total_revenue or 0.0,
        "ordersPerStatus": status_counts
    }