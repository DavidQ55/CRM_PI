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

        role = "empleado"
        
        total_users = conn.execute(
            "SELECT COUNT(*) as total FROM users"
        ).fetchone()["total"]

        role = "admin" if total_users == 0 else "empleado"
        
        cur = conn.execute(
            "INSERT INTO users(name, email, password, role) VALUES(?, ?, ?, ?)",
            (name, email, password, role)
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
            "SELECT id, name, email, role FROM users WHERE email = ? AND password = ?",
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
        
@router.put("/users/{user_id}/role")
def update_role(user_id: int, data: dict):

    conn = get_conn()

    try:
        current_user_role = data.get("current_user_role")
        new_role = data.get("role")

        if current_user_role != "admin":
            raise HTTPException(403, "No tienes permisos")

        if new_role not in ["admin", "empleado"]:
            raise HTTPException(400, "Rol inválido")

        conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role, user_id)
        )

        conn.commit()

        return {"message": "Rol actualizado"}

    finally:
        conn.close()
        
