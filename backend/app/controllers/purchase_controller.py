from database.db import get_conn
from datetime import datetime

def add_purchase(p):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO purchases(client_id, amount, date) VALUES(?, ?, ?)",
            (p.client_id, p.amount, datetime.now().isoformat())
        )
        conn.commit()

        classify_client(p.client_id)
        return True
    finally:
        conn.close()


def get_purchases(client_id):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM purchases WHERE client_id=? ORDER BY date DESC",
            (client_id,)
        ).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_purchase(purchase_id):
    conn = get_conn()
    try:
        client_id = conn.execute(
            "SELECT client_id FROM purchases WHERE id=?",
            (purchase_id,)
        ).fetchone()["client_id"]

        conn.execute(
            "DELETE FROM purchases WHERE id=?",
            (purchase_id,)
        )
        conn.commit()

        classify_client(client_id)

    finally:
        conn.close()

def classify_client(client_id):
    conn = get_conn()
    try:
        total = conn.execute("""
            SELECT COUNT(*) as total
            FROM purchases
            WHERE client_id=?
            AND date >= datetime('now','-30 days')
        """, (client_id,)).fetchone()["total"]

        if total >= 10:
            segment = "VIP"
        elif total >= 5:
            segment = "Frecuente"
        else:
            segment = "General"

        conn.execute(
            "UPDATE clients SET segment=? WHERE id=?",
            (segment, client_id)
        )
        conn.commit()
    finally:
        conn.close()


# 5 Mejores clientes (los 5 que más compras tienen)        
def top_clients():
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT c.id, c.name, COUNT(p.id) as total
            FROM clients c
            LEFT JOIN purchases p ON c.id = p.client_id
            GROUP BY c.id
            ORDER BY total DESC
            LIMIT 5
        """).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()