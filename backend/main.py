from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes import clients, purchases, users
from database.db import init_db

app = FastAPI(title="CRM Clientes API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

init_db()

@app.get("/")
def home():
    return FileResponse("../frontend/public/index.html")

app.include_router(clients.router)
app.include_router(purchases.router)
app.include_router(users.router)