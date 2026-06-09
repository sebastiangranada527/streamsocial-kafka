"""API REST de StreamSocial con FastAPI.

Expone endpoints para publicar eventos (via el productor) y consultar
los eventos procesados (via el consumidor, que corre en segundo plano).
"""

import logging
import threading
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import (
    ContentLikeRequest,
    PublishResponse,
    UserRegisterRequest,
)
from consumers.event_consumer import StreamSocialEventConsumer
from models.events import EventType, StreamSocialEvent
from producers.event_producer import StreamSocialEventProducer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Objetos globales que viviran mientras la app este corrienda.
# Se inicializan en el lifespan (al arrancar la app).
producer: Optional[StreamSocialEventProducer] = None
consumer: Optional[StreamSocialEventConsumer] = None


def _run_consumer(consumer: StreamSocialEventConsumer) -> None:
    """Bucle del consumidor. Corre en un hilo aparte para no bloquear la API."""
    try:
        consumer.consume()  # sin max_messages -> escucha indefinidamente
    except Exception as exc:  # noqa: BLE001
        logger.error("El consumidor se detuvo: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la app: setup al arrancar, limpieza al apagar.

    Todo lo ANTES del 'yield' se ejecuta al arrancar.
    Todo lo DESPUES del 'yield' se ejecuta al apagar.
    """
    global producer, consumer

    # --- Arranque ---
    logger.info("Iniciando productor y consumidor...")
    producer = StreamSocialEventProducer()
    # Solo eventos nuevos a partir de ahora (no reprocesar historico)
    consumer = StreamSocialEventConsumer(from_beginning=False)

    # Lanzar el consumidor en un hilo de fondo (daemon = muere con la app)
    hilo = threading.Thread(
        target=_run_consumer, args=(consumer,), daemon=True
    )
    hilo.start()

    yield  # <-- aqui la app queda corriendo, atendiendo peticiones

    # --- Apagado ---
    logger.info("Cerrando productor y consumidor...")
    if producer:
        producer.close()
    if consumer:
        consumer.close()


# Crear la app, registrando el lifespan
app = FastAPI(title="StreamSocial API", lifespan=lifespan)

# CORS: permite que el frontend (otro origen, ej: localhost:5173)
# pueda llamar a esta API sin que el navegador lo bloquee.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en produccion se restringe a dominios concretos
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Endpoint de salud: confirma que la API esta viva."""
    return {"status": "ok", "service": "StreamSocial API"}


@app.post("/events/user/register", response_model=PublishResponse)
def register_user(req: UserRegisterRequest):
    """Publica un evento de registro de usuario."""
    if producer is None:
        raise HTTPException(status_code=503, detail="Productor no disponible")

    evento = StreamSocialEvent(
        event_type=EventType.USER_REGISTRATION,
        user_id=req.user_id,
        data={"email": req.email, "plan": req.plan},
    )
    result = producer.publish(evento)
    return PublishResponse(success=True, **result)


@app.post("/events/content/like", response_model=PublishResponse)
def like_content(req: ContentLikeRequest):
    """Publica un evento de 'like' a un contenido."""
    if producer is None:
        raise HTTPException(status_code=503, detail="Productor no disponible")

    evento = StreamSocialEvent(
        event_type=EventType.CONTENT_LIKE,
        user_id=req.user_id,
        data={"post_id": req.post_id},
    )
    result = producer.publish(evento)
    return PublishResponse(success=True, **result)


@app.get("/events/recent")
def recent_events(limit: int = 20):
    """Devuelve los eventos mas recientes procesados por el consumidor."""
    if consumer is None:
        return {"events": [], "total": 0}

    # Los ultimos 'limit' eventos, del mas reciente al mas antiguo
    eventos = consumer.processed_events[-limit:][::-1]
    return {"events": eventos, "total": len(consumer.processed_events)}
