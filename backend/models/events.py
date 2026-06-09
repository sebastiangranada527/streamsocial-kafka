"""Modelos de eventos de StreamSocial.

Define la estructura (contrato) que comparten el productor y el consumidor.
Todo evento que circula por Kafka debe ajustarse a estos modelos.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Tipos de eventos permitidos en StreamSocial.

    Hereda de `str` para que el valor sea directamente un string
    (útil al serializar a JSON). Es una lista CERRADA: solo estos
    10 valores son válidos.
    """

    # --- Ciclo de vida del usuario ---
    USER_REGISTRATION = "user_registration"
    USER_LOGIN = "user_login"
    USER_PROFILE_UPDATE = "user_profile_update"
    USER_FOLLOW = "user_follow"

    # --- Contenido ---
    USER_POST_CREATE = "user_post_create"
    USER_POST_DELETE = "user_post_delete"

    # --- Interacciones ---
    CONTENT_LIKE = "content_like"
    CONTENT_COMMENT = "content_comment"
    CONTENT_SHARE = "content_share"

    # --- Sistema ---
    SYSTEM_NOTIFICATION = "system_notification"


class StreamSocialEvent(BaseModel):
    """Representa un evento que fluye por el sistema.

    Pydantic valida automáticamente cada campo según su tipo.
    Si alguien intenta crear un evento mal formado, lanza un error
    claro ANTES de que llegue a Kafka.
    """

    # default_factory genera un valor nuevo en cada instancia.
    # Sin él, todos los eventos compartirían el mismo id/timestamp.
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    user_id: str
    session_id: Optional[str] = None
    data: dict = Field(default_factory=dict)
