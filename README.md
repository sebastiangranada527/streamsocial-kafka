# StreamSocial — Event-Driven Architecture con Apache Kafka

Proyecto de aprendizaje práctico basado en el curso [Hands-on Kafka](https://handsonkafka.substack.com/p/day-1-event-driven-architecture-fundamentals). Construye una red social simulada para dominar los fundamentos de la arquitectura orientada a eventos.

## ¿Qué aprenderás?

- Por qué las arquitecturas síncronas tradicionales crean cuellos de botella
- Cómo diseñar un sistema de eventos con taxonomía clara
- Productores y consumidores de Kafka en Python
- Integración de Kafka con APIs REST (FastAPI)
- Visualización de streams de eventos en tiempo real (React)
- Buenas prácticas de desarrollo: CI/CD, linting, tests, variables de entorno

## Arquitectura

```
[Usuario] → [FastAPI] → [Kafka Producer] → [Kafka Broker]
                                                  ↓
                                        [Kafka Consumer]
                                                  ↓
                                    [Dashboard React] ← [GET /events/recent]
```

**Flujo de un evento:**
1. El usuario hace una acción (ej: registrarse)
2. El API publica un evento `user_registration` al topic `streamsocial-events`
3. El consumidor lo procesa y lo almacena en memoria
4. El dashboard React consulta los eventos cada 2 segundos y actualiza las métricas

## Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Message Broker | Apache Kafka | 7.5.0 |
| Coordinación | Zookeeper | 7.5.0 |
| API | FastAPI + Python | 3.9+ |
| Modelos | Pydantic | v2 |
| Cliente Kafka | kafka-python | 2.x |
| Frontend | React + Vite | 18+ |
| Tests | pytest | 7+ |
| Contenedores | Docker Compose | v3.8 |

## Requisitos Previos

- Docker Desktop instalado y corriendo
- Python 3.9+
- Node.js 18+

## Setup Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/sebastiangranada527/streamsocial-kafka.git
cd streamsocial-kafka

# 2. Configurar variables de entorno
cp .env.example .env

# 3. Levantar la infraestructura Kafka
make infra-up

# 4. Crear el topic
make topic-create

# 5. Instalar dependencias del backend
make backend-install

# 6. Iniciar el servidor API
make backend-run
```

La **Kafka UI** estará disponible en http://localhost:8080 para inspeccionar topics y mensajes en tiempo real.

## Estructura del Proyecto

```
streamsocial-kafka/
├── .github/workflows/ci.yml   # CI: tests automáticos en cada PR
├── backend/
│   ├── models/events.py       # Definición de eventos con Pydantic
│   ├── producers/             # Publicación de eventos a Kafka
│   ├── consumers/             # Procesamiento de eventos de Kafka
│   ├── api/main.py            # API FastAPI
│   └── tests/                 # Tests unitarios e integración
├── frontend/                  # Dashboard React
├── docs/architecture.md       # Decisiones de diseño y diagramas
├── docker-compose.yml         # Kafka + Zookeeper + Kafka UI
├── Makefile                   # Comandos de desarrollo
└── .env.example               # Template de configuración
```

## Taxonomía de Eventos

| Categoría | Tipo de Evento |
|---|---|
| Ciclo de vida de usuario | `user_registration`, `user_login`, `user_profile_update`, `user_follow` |
| Contenido | `user_post_create`, `user_post_delete` |
| Interacciones | `content_like`, `content_comment`, `content_share` |
| Sistema | `system_notification` |

## Comandos de Desarrollo

```bash
make help          # Ver todos los comandos disponibles
make infra-up      # Levantar Kafka
make infra-down    # Detener Kafka
make test          # Correr tests
make lint          # Correr linter
```

## Licencia

MIT
