from fastapi import APIRouter
from app.models.purchase import Purchase
from app.controllers import purchase_controller

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("")
def add_purchase(p: Purchase):
    purchase_controller.add_purchase(p)
    return {"message": "Compra registrada"}


@router.get("/{client_id}")
def get_purchases(client_id: int):
    return purchase_controller.get_purchases(client_id)