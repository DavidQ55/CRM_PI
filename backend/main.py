from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import sqlite3
import os

app = FastAPI(title="CRM Clientes API")

# -------------------------
# CONFIGURACIÓN DE RUTAS
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DATABASE_DIR = os.path.join(BASE_DIR, "backend", "database")

# -------------------------
# STATIC FILES (CSS y JS)
# -------------------------
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")),
    name="static"
)

# -------------------------
# CORS (permite conexión frontend-backend)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# BASE DE DATOS
# -------------------------
DB = os.path.join(DATABASE_DIR, "crm.db")


def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS clients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        segment TEXT NOT NULL DEFAULT 'General'
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


init_db()

# -------------------------
# MODELOS
# -------------------------
class Client(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    segment: str = "General"


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# -------------------------
# FRONTEND
# -------------------------
@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "public", "index.html"))


@app.get("/test")
def test():
    return {"message": "Backend funcionando correctamente"}


# -------------------------
# USUARIOS
# -------------------------
@app.post("/register")
def register(user: UserRegister):
    name = user.name.strip()
    email = str(user.email).strip().lower()
    password = user.password.strip()

    if not name or not email or not password:
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")

    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            raise HTTPException(status_code=400, detail="El usuario ya está registrado")

        cur = conn.execute(
            "INSERT INTO users(name, email, password) VALUES(?, ?, ?)",
            (name, email, password)
        )
        conn.commit()

        return {
            "message": "Usuario registrado correctamente",
            "id": cur.lastrowid
        }

    finally:
        conn.close()


@app.post("/login")
def login(user: UserLogin):
    email = str(user.email).strip().lower()
    password = user.password.strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="Ingrese correo y contraseña")

    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        if not existing:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        return {
            "message": "Inicio de sesión exitoso",
            "user": {
                "id": existing["id"],
                "name": existing["name"],
                "email": existing["email"]
            }
        }

    finally:
        conn.close()


# -------------------------
# CLIENTES
# -------------------------
@app.post("/clients")
def create_client(client: Client):
    name = client.name.strip() if client.name else ""
    email = str(client.email).strip().lower() if client.email else ""
    phone = client.phone.strip() if client.phone else ""
    segment = client.segment.strip() if client.segment else "General"

    if not name or not email or not phone:
        raise HTTPException(status_code=400, detail="Datos incompletos")

    conn = get_conn()

    try:
        cur = conn.execute(
            "INSERT INTO clients(name, email, phone, segment) VALUES(?, ?, ?, ?)",
            (name, email, phone, segment)
        )
        conn.commit()

        return {
            "message": "Cliente registrado correctamente",
            "id": cur.lastrowid
        }

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese correo")

    finally:
        conn.close()


@app.get("/clients")
def list_clients(search: str = "", segment: str = ""):
    conn = get_conn()

    try:
        query = "SELECT * FROM clients WHERE 1=1"
        params = []

        if search.strip():
            query += " AND name LIKE ?"
            params.append(f"%{search.strip()}%")

        if segment.strip():
            query += " AND segment = ?"
            params.append(segment.strip())

        query += " ORDER BY id DESC"

        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    finally:
        conn.close()


@app.put("/clients/{client_id}")
def update_client(client_id: int, client: Client):
    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT * FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        name = client.name.strip() if client.name else existing["name"]
        email = str(client.email).strip().lower() if client.email else existing["email"]
        phone = client.phone.strip() if client.phone else existing["phone"]
        segment = client.segment.strip() if client.segment else existing["segment"]

        if not name or not email or not phone:
            raise HTTPException(status_code=400, detail="Datos inválidos para actualizar")

        conn.execute(
            "UPDATE clients SET name = ?, email = ?, phone = ?, segment = ? WHERE id = ?",
            (name, email, phone, segment, client_id)
        )
        conn.commit()

        return {"message": "Cliente actualizado correctamente"}

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Ya existe un cliente con ese correo")

    finally:
        conn.close()


@app.delete("/clients/{client_id}")
def delete_client(client_id: int):
    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT id FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        if not existing:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        conn.execute(
            "DELETE FROM clients WHERE id = ?",
            (client_id,)
        )
        conn.commit()

        return {"message": "Cliente eliminado correctamente"}

    finally:
        conn.close()