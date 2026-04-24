from fastapi import APIRouter, HTTPException
from app.models.user import UserRegister, UserLogin
from database.db import get_conn

router = APIRouter()


@router.post("/register")
def register(user: UserRegister):
    name = user.name.strip()
    email = str(user.email).strip().lower()
    password = user.password.strip()

    if not name or not email or not password:
        raise HTTPException(400, "Todos los campos son obligatorios")

    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            raise HTTPException(400, "El usuario ya está registrado")

        cur = conn.execute(
            "INSERT INTO users(name, email, password) VALUES(?, ?, ?)",
            (name, email, password)
        )
        conn.commit()

        return {"message": "Usuario registrado", "id": cur.lastrowid}

    finally:
        conn.close()


@router.post("/login")
def login(user: UserLogin):
    email = str(user.email).strip().lower()
    password = user.password.strip()

    if not email or not password:
        raise HTTPException(400, "Ingrese correo y contraseña")

    conn = get_conn()

    try:
        existing = conn.execute(
            "SELECT id, name, email FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        if not existing:
            raise HTTPException(401, "Credenciales incorrectas")

        return {
            "message": "Inicio de sesión exitoso",
            "user": dict(existing)
        }

    finally:
        conn.close()