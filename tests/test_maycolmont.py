from app import cli
from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_pago_rechazado_top_down(mocker, capsys, requests_mock):
    """
    Prueba de integración top-down: empieza en la capa superior (CLI) e incorpora
    hacia abajo OrderService y PaymentGateway reales. Se sustituye el conector de
    base de datos por FakeDb y la respuesta HTTP del proveedor por requests_mock
    con un 402. Debe comprobar que el rechazo llega al usuario, que el pedido no
    se registra y que el inventario se conserva, según el flujo del README.
    """
    db = FakeDb(stock={"CUADERNO": 9}, prices={"CUADERNO": 10.0})
    gateway = PaymentGateway(base_url="https://payments.example.com/api/v1")
    mocker.patch("app.cli.build_service", return_value=OrderService(db, gateway))
    requests_mock.post(
        "https://payments.example.com/api/v1/charges",
        status_code=402,
        json={"reason": "insufficient_funds"},
    )

    mocker.patch("builtins.input", side_effect=["cuaderno", "2", "tok-maycolmont"])
    codigo = cli.main()
    salida = capsys.readouterr().out

    assert codigo == 1, salida
    assert "ERROR: pago rechazado" in salida, salida
    assert db.orders == {}, salida
    assert db.get_stock("CUADERNO") == 9, salida
    assert requests_mock.last_request.json() == {
        "card_token": "tok-maycolmont",
        "amount": 23.2,
    }
