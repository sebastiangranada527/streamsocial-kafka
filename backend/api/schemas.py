"""Modelos de request/response de la API.

Definen y validan la forma de los datos que entran y salen de los
endpoints. FastAPI los usa para validacion automatica y documentacion.
"""

from pydantic import BaseModel


class UserRegisterRequest(BaseModel):
    """Datos para registrar un usuario."""

    user_id: str
    email: str
    plan: str = "free"  # valor por defecto si no se envia


class ContentLikeRequest(BaseModel):
    """Datos para registrar un 'like' a un contenido."""

    user_id: str
    post_id: str


class PublishResponse(BaseModel):
    """Respuesta tras publicar un evento."""

    success: bool
    event_id: str
    partition: int
    offset: int
