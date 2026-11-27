from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pago_aprobado_registra_pedido_bottom_up(requests_mock):
    """
    Prueba de integración bottom-up: parte de las capas internas 
    (OrderService, PaymentGateway). Se usa FakeDb y requests_mock
    para validar el cálculo del total, el payload enviado, el parseo de la
    respuesta 200 OK y la persistencia del pedido.
    """
    db = FakeDb(stock={"CUADERNO": 9}, prices={"CUADERNO": 10.0})
    gateway = PaymentGateway(base_url="https://payments.example.com/api/v1")
    service = OrderService(db, gateway)

    requests_mock.post(
        "https://payments.example.com/api/v1/charges",
        status_code=200,
        json={"transaction_id": "tx-cpalma"},
    )

    result = service.place_order("CUADERNO", 2, "tok-cpalma")

    assert result == {
        "order_id": "ORD-1",
        "total": 23.2,
        "status": "CONFIRMED",
    }
    assert db.orders["ORD-1"] == {
        "product_id": "CUADERNO",
        "quantity": 2,
        "total": 23.2,
        "transaction_id": "tx-cpalma",
    }
    assert requests_mock.last_request.json() == {
        "card_token": "tok-cpalma",
        "amount": 23.2,
    }