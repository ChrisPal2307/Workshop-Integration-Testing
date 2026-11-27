import pytest
from app.order_service import OrderService, OutOfStockError
from app.payment_gateway import PaymentGateway
from tests.support.fake_db import FakeDb


def test_stock_insuficiente_no_cobra_ni_persiste_bottom_up(mocker):
    # 1. Preparación: producto con 2 unidades en stock
    db = FakeDb(stock={"LIBRO": 2}, prices={"LIBRO": 15.0})
    pasarela = mocker.Mock(spec=PaymentGateway)
    servicio = OrderService(db, pasarela)

    # 2. Ejecución y comprobación de la excepción
    with pytest.raises(OutOfStockError) as exc_info:
        servicio.place_order("LIBRO", 5, "tok_prueba")

    # 3. Verificaciones de integración
    assert "Stock insuficiente para 'LIBRO'" in str(exc_info.value)
    # Comprobar que NUNCA se intentó cobrar a la pasarela
    pasarela.charge.assert_not_called()
    # Comprobar que no se guardó la orden y el stock no cambió
    assert len(db.orders) == 0
    assert db.get_stock("LIBRO") == 2