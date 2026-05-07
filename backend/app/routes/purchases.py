from fastapi import APIRouter, Query
from app.models.purchase import Purchase
from app.controllers import purchase_controller
from app.controllers.purchase_controller import (top_clients_by_date, clients_by_segment)

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


@router.get("/dashboard")
def dashboard_metrics(
    start: str = Query(None),
    end: str = Query(None)
):

    if start and end and start > end:
        return {
            "error": "La fecha inicial no puede ser mayor"
        }

    return {
        "top_clients": top_clients_by_date(start, end),
        "segments": clients_by_segment(start, end)
    }
