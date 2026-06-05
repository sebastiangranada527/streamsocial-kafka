"""Tests del StreamSocialEventProducer usando mocks.

No se conecta a un Kafka real: reemplaza KafkaProducer por un mock
para verificar que nuestro productor lo usa correctamente.
"""

from unittest.mock import MagicMock, patch

from models.events import EventType, StreamSocialEvent
from producers.event_producer import StreamSocialEventProducer


@patch("producers.event_producer.KafkaProducer")
def test_publish_envia_al_topic_correcto(mock_kafka_producer_class):
    """El productor debe enviar el evento al topic con la key correcta."""
    # Configurar el mock: simular la metadata que devuelve Kafka
    mock_instance = mock_kafka_producer_class.return_value
    mock_metadata = MagicMock()
    mock_metadata.partition = 2
    mock_metadata.offset = 0
    mock_instance.send.return_value.get.return_value = mock_metadata

    # Crear el productor (usará el mock en vez del KafkaProducer real)
    producer = StreamSocialEventProducer()
    evento = StreamSocialEvent(
        event_type=EventType.USER_REGISTRATION,
        user_id="user_alice",
    )

    resultado = producer.publish(evento)

    # Verificar que send() se llamó con el topic y la key correctos
    mock_instance.send.assert_called_once()
    _, kwargs = mock_instance.send.call_args
    assert kwargs["topic"] == "streamsocial-events"
    assert kwargs["key"] == "user_alice"

    # Verificar que devuelve la metadata esperada
    assert resultado["partition"] == 2
    assert resultado["offset"] == 0
    assert resultado["event_id"] == evento.event_id


@patch("producers.event_producer.KafkaProducer")
def test_publish_serializa_el_evento_completo(mock_kafka_producer_class):
    """El value enviado debe contener los datos del evento."""
    mock_instance = mock_kafka_producer_class.return_value
    mock_instance.send.return_value.get.return_value = MagicMock(
        partition=0, offset=0
    )

    producer = StreamSocialEventProducer()
    evento = StreamSocialEvent(
        event_type=EventType.CONTENT_LIKE,
        user_id="user_bob",
        data={"post_id": "post_123"},
    )

    producer.publish(evento)

    # El value enviado debe incluir los campos del evento
    _, kwargs = mock_instance.send.call_args
    value = kwargs["value"]
    assert value["user_id"] == "user_bob"
    assert value["event_type"] == "content_like"
    assert value["data"]["post_id"] == "post_123"
