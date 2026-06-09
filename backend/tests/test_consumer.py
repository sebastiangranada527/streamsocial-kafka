"""Tests del StreamSocialEventConsumer usando mocks.

Mockea KafkaConsumer para no conectarse a un broker real. Se enfoca
en verificar la logica de registro y despacho de handlers.
"""

from unittest.mock import patch

from consumers.event_consumer import StreamSocialEventConsumer
from models.events import EventType


@patch("consumers.event_consumer.KafkaConsumer")
def test_register_handler_asocia_funcion_a_tipo(mock_consumer_class):
    """register_handler debe guardar el handler bajo su tipo de evento."""
    consumer = StreamSocialEventConsumer()

    def mi_handler(event):
        pass

    consumer.register_handler(EventType.USER_REGISTRATION, mi_handler)

    # El handler debe estar registrado para ese tipo
    assert mi_handler in consumer._handlers[EventType.USER_REGISTRATION]


@patch("consumers.event_consumer.KafkaConsumer")
def test_dispatch_ejecuta_el_handler_correcto(mock_consumer_class):
    """Al despachar un evento, se ejecuta el handler de su tipo."""
    consumer = StreamSocialEventConsumer()

    # Lista para capturar lo que recibe el handler
    recibidos = []
    consumer.register_handler(
        EventType.CONTENT_LIKE, lambda e: recibidos.append(e)
    )

    # Simular la llegada de un evento de tipo content_like
    evento = {"event_type": "content_like", "user_id": "user_x", "data": {}}
    consumer._dispatch(evento)

    # El handler debe haberse ejecutado con ese evento
    assert len(recibidos) == 1
    assert recibidos[0]["user_id"] == "user_x"


@patch("consumers.event_consumer.KafkaConsumer")
def test_dispatch_guarda_evento_procesado(mock_consumer_class):
    """Cada evento despachado se acumula en processed_events."""
    consumer = StreamSocialEventConsumer()

    evento = {"event_type": "user_login", "user_id": "user_y", "data": {}}
    consumer._dispatch(evento)

    assert len(consumer.processed_events) == 1
    assert consumer.processed_events[0]["user_id"] == "user_y"


@patch("consumers.event_consumer.KafkaConsumer")
def test_dispatch_ignora_tipo_desconocido(mock_consumer_class):
    """Un evento con tipo invalido no se procesa ni rompe el consumidor."""
    consumer = StreamSocialEventConsumer()

    evento = {"event_type": "tipo_inexistente", "user_id": "user_z", "data": {}}
    consumer._dispatch(evento)

    # No debe guardarse porque el tipo es desconocido
    assert len(consumer.processed_events) == 0


@patch("consumers.event_consumer.KafkaConsumer")
def test_un_handler_no_afecta_otro_tipo(mock_consumer_class):
    """Un handler registrado para un tipo NO se ejecuta para otro tipo."""
    consumer = StreamSocialEventConsumer()

    likes = []
    consumer.register_handler(EventType.CONTENT_LIKE, lambda e: likes.append(e))

    # Despachar un evento de OTRO tipo
    consumer._dispatch(
        {"event_type": "user_login", "user_id": "u", "data": {}}
    )

    # El handler de likes no debe haberse ejecutado
    assert len(likes) == 0
