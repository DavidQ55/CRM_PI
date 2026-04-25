from app.controllers import client_controller, purchase_controller
from types import SimpleNamespace



def test_add_purchase():
    client = SimpleNamespace(
        name="Test",
        email="test_unique@test.com",
        phone="123",
        segment="General",
        notes=""
    )

    client_id = client_controller.create_client(client)

    data = SimpleNamespace(
        client_id=client_id,
        amount=1
    )

    result = purchase_controller.add_purchase(data)

    assert result == True


def test_get_purchases():
    result = purchase_controller.get_purchases(1)
    assert isinstance(result, list)


def test_delete_purchase():
    # primero creamos una compra
    data = SimpleNamespace(client_id=1, amount=1)
    purchase_controller.add_purchase(data)

    purchases = purchase_controller.get_purchases(1)

    if purchases:
        purchase_id = purchases[0]["id"]
        purchase_controller.delete_purchase(purchase_id)

        updated = purchase_controller.get_purchases(1)
        assert isinstance(updated, list)


def test_top_clients():
    result = purchase_controller.top_clients()

    assert isinstance(result, list)

    if result:
        assert "name" in result[0]
        assert "total" in result[0]