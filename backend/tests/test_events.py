"""Tests del modelo de eventos StreamSocialEvent."""

import pytest
from pydantic import ValidationError

from models.events import EventType, StreamSocialEvent


def test_evento_se_crea_con_campos_minimos():
    """Un evento válido se crea pasando solo event_type y user_id."""
    evento = StreamSocialEvent(
        event_type=EventType.USER_REGISTRATION,
        user_id="user_001",
    )
    assert evento.user_id == "user_001"
    assert evento.event_type == EventType.USER_REGISTRATION


def test_event_id_y_timestamp_se_autogeneran():
    """event_id y timestamp deben generarse automáticamente."""
    evento = StreamSocialEvent(
        event_type=EventType.USER_LOGIN,
        user_id="user_002",
    )
    # event_id no debe estar vacío
    assert evento.event_id
    # timestamp debe existir
    assert evento.timestamp is not None


def test_dos_eventos_tienen_ids_distintos():
    """Cada evento debe tener un event_id único."""
    e1 = StreamSocialEvent(event_type=EventType.CONTENT_LIKE, user_id="u1")
    e2 = StreamSocialEvent(event_type=EventType.CONTENT_LIKE, user_id="u1")
    assert e1.event_id != e2.event_id


def test_tipo_de_evento_invalido_es_rechazado():
    """Un event_type fuera del enum debe lanzar ValidationError."""
    with pytest.raises(ValidationError):
        StreamSocialEvent(event_type="tipo_inventado", user_id="u1")


def test_serializacion_a_json_funciona():
    """El evento debe poder serializarse a JSON sin errores."""
    evento = StreamSocialEvent(
        event_type=EventType.CONTENT_COMMENT,
        user_id="user_003",
        data={"comment": "hola"},
    )
    json_str = evento.model_dump_json()
    assert "content_comment" in json_str
    assert "user_003" in json_str
