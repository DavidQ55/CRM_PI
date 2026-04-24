from fastapi import APIRouter
from app.models.purchase import Purchase
from app.controllers import purchase_controller

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("")
def add_purchase(p: Purchase):
    purchase_controller.add_purchase(p)
    return {"message": "Compra registrada"}


# Top clientes
@router.get("/top")
def get_top_clients():
    return purchase_controller.top_clients()

@router.get("/{client_id}")
def get_purchases(client_id: int):
    return purchase_controller.get_purchases(client_id)


@router.delete("/{purchase_id}")
def delete_purchase(purchase_id: int):
    purchase_controller.delete_purchase(purchase_id)
    return {"message": "Compra eliminada"}


