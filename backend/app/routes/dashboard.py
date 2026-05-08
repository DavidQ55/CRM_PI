from fastapi import APIRouter
from app.controllers.dashboard_controller import get_dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
def dashboard(start_date: str = None, end_date: str = None):
    return get_dashboard_metrics(start_date, end_date)