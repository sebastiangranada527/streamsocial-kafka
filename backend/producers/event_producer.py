"""Productor de eventos de StreamSocial.

Encapsula la conexión a Kafka y la publicación de eventos al topic.
Convierte un objeto StreamSocialEvent en bytes y lo envía al broker.
"""

import json
import logging

from kafka import KafkaProducer

import config
from models.events import StreamSocialEvent

logger = logging.getLogger(__name__)


class StreamSocialEventProducer:
    """Publica eventos de StreamSocial al topic de Kafka."""

    def __init__(self) -> None:
        # KafkaProducer es el cliente que se conecta al broker.
        self._producer = KafkaProducer(
            # Dirección del broker (de nuestra config).
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,

            # value_serializer: convierte el VALOR del mensaje a bytes.
            # Kafka solo transmite bytes, así que: dict -> JSON -> bytes UTF-8
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),

            # key_serializer: convierte la CLAVE a bytes.
            # La clave (user_id) decide a qué partición va el evento.
            key_serializer=lambda k: k.encode("utf-8") if k else None,

            # acks="all": espera confirmación de que el evento se guardó
            # de forma segura antes de considerarlo enviado. Más fiable.
            acks="all",
        )

    def publish(self, event: StreamSocialEvent) -> dict:
        """Publica un evento y devuelve metadata de dónde quedó guardado.

        Args:
            event: el evento a publicar.

        Returns:
            dict con event_id, partición y offset asignados por Kafka.
        """
        # Convertimos el modelo Pydantic a un dict serializable a JSON.
        # mode="json" asegura que tipos como datetime se vuelvan strings.
        payload = event.model_dump(mode="json")

        # send() es ASÍNCRONO: encola el mensaje y devuelve un "future".
        future = self._producer.send(
            topic=config.KAFKA_TOPIC,
            key=event.user_id,   # clave de partición
            value=payload,
        )

        # .get(timeout=10) BLOQUEA hasta que Kafka confirme (o falle).
        # Nos devuelve la metadata: partición y offset reales.
        metadata = future.get(timeout=10)

        logger.info(
            "Evento publicado: %s -> particion %s, offset %s",
            event.event_type, metadata.partition, metadata.offset,
        )

        return {
            "event_id": event.event_id,
            "partition": metadata.partition,
            "offset": metadata.offset,
        }

    def close(self) -> None:
        """Cierra la conexión con el broker, vaciando mensajes pendientes."""
        self._producer.flush()
        self._producer.close()
