from pydantic import BaseModel

class Purchase(BaseModel):
    client_id: int
    amount: float