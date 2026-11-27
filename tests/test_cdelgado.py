import pytest

from app.order_service import OrderService
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_cantidad_cero_no_cobra_ni_persiste_bottom_up(mocker):
    """
    Estrategia: bottom-up. Se prueba OrderService con FakeDb y una pasarela
    simulada para confirmar que una cantidad inválida se rechaza antes del cobro.
    """
    db = FakeDb(stock={"CUADERNO": 9}, prices={"CUADERNO": 10.0})
    gateway = mocker.Mock(spec=PaymentGateway)
    service = OrderService(db, gateway)

    with pytest.raises(ValueError, match="La cantidad debe ser un entero positivo"):
        service.place_order("CUADERNO", 0, "tok-cdelgado")

    gateway.charge.assert_not_called()
    assert db.orders == {}
    assert db.get_stock("CUADERNO") == 9
