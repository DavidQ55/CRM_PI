from fastapi import APIRouter, HTTPException
from app.models.client import Client
from app.controllers import client_controller

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("")
def create(client: Client):
    result = client_controller.create_client(client)
    if not result:
        raise HTTPException(400, "Cliente ya existe")
    return {"message": "Cliente creado"}


@router.get("")
def list_clients(search: str = "", segment: str = ""):
    return client_controller.get_clients(search, segment)


@router.put("/{client_id}")
def update(client_id: int, client: Client):
    ok = client_controller.update_client(client_id, client)
    if not ok:
        raise HTTPException(404, "Cliente no encontrado")
    return {"message": "Actualizado"}


@router.delete("/{client_id}")
def delete(client_id: int):
    client_controller.delete_client(client_id)
    return {"message": "Eliminado"}