"""Configuración central del backend.

Lee las variables de entorno desde el archivo .env y las expone
como constantes. Así el código nunca tiene valores "hardcodeados":
la configuración cambia entre entornos (local, producción) sin
tocar el código.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el .env que está en la raíz del proyecto.
# __file__ = este archivo (backend/config.py)
# .parent = backend/   .parent.parent = raíz del proyecto
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env")

# --- Kafka ---
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "streamsocial-events")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "streamsocial-consumers")
