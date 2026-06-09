"""Tests de la API de StreamSocial.

Usa TestClient de FastAPI para simular peticiones HTTP sin levantar
un servidor real. Mockea el productor para no depender de Kafka.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Crea un TestClient con productor y consumidor mockeados.

    Parchea las clases ANTES de importar la app, para que el lifespan
    cree los mocks en vez de los objetos reales que necesitan Kafka.
    """
    with patch("api.main.StreamSocialEventProducer") as mock_prod_class, \
         patch("api.main.StreamSocialEventConsumer") as mock_cons_class:

        # Configurar el productor mock: publish() devuelve metadata falsa
        mock_producer = mock_prod_class.return_value
        mock_producer.publish.return_value = {
            "event_id": "test-id-123",
            "partition": 1,
            "offset": 5,
        }

        # Configurar el consumidor mock: lista de eventos vacia
        mock_consumer = mock_cons_class.return_value
        mock_consumer.processed_events = []
        # consume() no debe bloquear en los tests
        mock_consumer.consume = MagicMock()

        # Importar la app DESPUES de los patches
        from api.main import app

        with TestClient(app) as test_client:
            yield test_client


def test_root_endpoint(client):
    """El endpoint raiz confirma que la API esta viva."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_user(client):
    """POST /events/user/register debe publicar y devolver metadata."""
    response = client.post(
        "/events/user/register",
        json={"user_id": "user_test", "email": "test@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["event_id"] == "test-id-123"
    assert data["partition"] == 1
    assert data["offset"] == 5


def test_register_user_falla_sin_datos(client):
    """Sin los campos requeridos, la API devuelve error de validacion 422."""
    response = client.post("/events/user/register", json={})
    assert response.status_code == 422


def test_like_content(client):
    """POST /events/content/like debe publicar un like."""
    response = client.post(
        "/events/content/like",
        json={"user_id": "user_test", "post_id": "post_99"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_recent_events_vacio(client):
    """GET /events/recent devuelve lista vacia si no hay eventos."""
    response = client.get("/events/recent")
    assert response.status_code == 200
    data = response.json()
    assert data["events"] == []
    assert data["total"] == 0
