"""Consumidor de eventos de StreamSocial.

Se suscribe al topic de Kafka, deserializa los eventos recibidos y
los despacha a handlers (funciones) registrados por tipo de evento.
"""

import json
import logging
from typing import Callable, Dict, List, Optional

from kafka import KafkaConsumer

import config
from models.events import EventType

logger = logging.getLogger(__name__)

# Un handler es una función que recibe un evento (dict) y no retorna nada.
EventHandler = Callable[[dict], None]


class StreamSocialEventConsumer:
    """Consume eventos del topic de Kafka y los procesa con handlers."""

    def __init__(self, from_beginning: bool = True) -> None:
        # auto_offset_reset controla DESDE DÓNDE leer si no hay offset previo:
        #   "earliest" -> desde el primer mensaje (lee el historico completo)
        #   "latest"   -> solo mensajes nuevos a partir de ahora
        offset_reset = "earliest" if from_beginning else "latest"

        self._consumer = KafkaConsumer(
            config.KAFKA_TOPIC,
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,

            # group_id: identifica el consumer group. Kafka reparte las
            # particiones entre los consumidores que compartan este id.
            group_id=config.KAFKA_GROUP_ID,

            auto_offset_reset=offset_reset,

            # value_deserializer: convierte los bytes recibidos de vuelta
            # a un dict de Python (bytes -> JSON -> dict).
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),

            # key_deserializer: la clave (user_id) tambien viene en bytes.
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
        )

        # Registro de handlers: {tipo_de_evento: [funcion1, funcion2, ...]}
        self._handlers: Dict[EventType, List[EventHandler]] = {}

        # Lista de eventos ya procesados (la usara el dashboard luego).
        self.processed_events: List[dict] = []

    def register_handler(
        self, event_type: EventType, handler: EventHandler
    ) -> None:
        """Registra una funcion para que se ejecute ante un tipo de evento.

        Patron de suscripcion: en vez de un if/else gigante, cada handler
        se asocia a un tipo de evento. Asi el codigo es extensible.
        """
        self._handlers.setdefault(event_type, []).append(handler)
        logger.info("Handler registrado para %s", event_type.value)

    def _dispatch(self, event: dict) -> None:
        """Ejecuta los handlers registrados para el tipo de evento recibido."""
        event_type_str = event.get("event_type")
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            logger.warning("Tipo de evento desconocido: %s", event_type_str)
            return

        # Guardar el evento procesado
        self.processed_events.append(event)

        # Ejecutar cada handler registrado para ese tipo
        for handler in self._handlers.get(event_type, []):
            handler(event)

    def consume(self, max_messages: Optional[int] = None) -> None:
        """Lee eventos del topic y los procesa.

        Args:
            max_messages: si se indica, se detiene tras procesar esa
                cantidad. Si es None, consume indefinidamente (bloquea).
        """
        logger.info("Consumidor escuchando el topic '%s'...", config.KAFKA_TOPIC)
        count = 0
        for message in self._consumer:
            self._dispatch(message.value)
            count += 1
            logger.info(
                "Procesado: %s (particion %s, offset %s)",
                message.value.get("event_type"),
                message.partition,
                message.offset,
            )
            if max_messages is not None and count >= max_messages:
                break

    def close(self) -> None:
        """Cierra la conexion con el broker."""
        self._consumer.close()
