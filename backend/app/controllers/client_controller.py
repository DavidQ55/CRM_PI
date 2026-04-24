from database.db import get_conn
import sqlite3

def create_client(data):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO clients(name, email, phone, segment) VALUES(?, ?, ?, ?)",
            (data.name, data.email, data.phone, data.segment)
        )
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_clients(search="", segment=""):
    conn = get_conn()
    try:
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")

        if segment:
            query += " AND segment = ?"
            params.append(segment)

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def update_client(client_id, data):
    conn = get_conn()
    try:
        existing = conn.execute(
            "SELECT * FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if not existing:
            return False

        conn.execute(
            "UPDATE clients SET name=?, email=?, phone=?, segment=? WHERE id=?",
            (data.name, data.email, data.phone, data.segment, client_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def delete_client(client_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        return True
    finally:
        conn.close()