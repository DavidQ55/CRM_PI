from app.controllers import client_controller
from types import SimpleNamespace
import time

def test_create_client():
    unique_email = f"test_{int(time.time())}@test.com"

    data = SimpleNamespace(
        name="Test User 2",
        email=unique_email,
        phone="123456",
        segment="General",
        notes="nota test"
    )

    result = client_controller.create_client(data)

    assert result is not None


def test_get_clients():
    clients = client_controller.get_clients()
    assert isinstance(clients, list)


def test_update_client():
    data = SimpleNamespace(
        name="Updated",
        email="updated@test.com",
        phone="999",
        segment="VIP",
        notes="updated note"
    )

    result = client_controller.update_client(1, data)

    assert result in [True, False]


def test_delete_client():
    result = client_controller.delete_client(1)
    assert result == True
    
    
def test_get_clients_with_filters():
    result = client_controller.get_clients(search="Test", segment="General")
    assert isinstance(result, list)