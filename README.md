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
                 POST /events/...
   [Dashboard React] ──────────────► [FastAPI]
          ▲                              │
          │                             publish
          │ GET /events/recent           ▼
          │                        [Kafka Producer]
          │                              │
          │                              ▼
          │                        [Kafka Broker]
          │                        topic: streamsocial-events
          │                        (3 particiones)
          │                              │
          │                              ▼
          └───────[FastAPI]◄──────[Kafka Consumer]
              processed_events     (hilo en segundo plano)
```

**Flujo de un evento:**
1. El usuario hace una acción en el dashboard (ej: registrarse)
2. El dashboard llama al API, que publica un evento `user_registration` al topic `streamsocial-events` usando el `user_id` como clave de partición
3. El consumidor (en un hilo de fondo) lo lee y lo almacena en memoria (`processed_events`)
4. El dashboard React consulta `GET /events/recent` cada 2 segundos (polling) y actualiza las métricas en vivo

## Stack Tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Message Broker | Apache Kafka | 7.5.0 |
| Coordinación | Zookeeper | 7.5.0 |
| API | FastAPI + Python | 3.9 |
| Modelos | Pydantic | v2 |
| Cliente Kafka | kafka-python | 2.0 |
| Frontend | React / Vite | 19 / 8 |
| Tests | pytest | 8 |
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


### Levantar el Frontend (Dashboard)

En una terminal aparte, con el backend ya corriendo:

```bash
cd frontend
npm install      # solo la primera vez
npm run dev
```

El dashboard estará disponible en **http://localhost:5173**. Haz click en "Generar registro de usuario" y observa los eventos fluir en tiempo real.

### El stack completo corriendo

Para ver todo el sistema funcionando necesitas **3 procesos**:

| Proceso | Puerto | Comando |
|---|---|---|
| Kafka (Docker) | 9092 | `make infra-up` |
| Backend (API) | 8000 | `make backend-run` |
| Frontend (Dashboard) | 5173 | `cd frontend && npm run dev` |

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

## Tests

El backend cuenta con 17 tests unitarios que cubren modelos, productor, consumidor y API.
Los tests usan **mocks** para no depender de un Kafka real, por lo que corren en milisegundos
y se ejecutan automáticamente en cada PR vía GitHub Actions.

```bash
make test
# o directamente:
cd backend && pytest tests/ -v
```

## Recorrido del Proyecto

Construido en 7 fases incrementales, cada una integrada vía Pull Request con CI en verde:

| Fase | Entregable | Conceptos clave |
|---|---|---|
| 1 | Infraestructura Kafka (Docker) | Broker, Zookeeper, topics, particiones |
| 2 | Modelos de eventos (Pydantic) | Contrato de eventos, serialización, taxonomía |
| 3 | Productor | Clave de partición, offsets, `acks`, serialización |
| 4 | Consumidor | Consumer groups, retención, handlers, offsets commiteados |
| 5 | API REST (FastAPI) | Endpoints, hilo de fondo, lifespan, CORS |
| 6 | Dashboard (React) | `useState`, `useEffect`, polling, integración full-stack |
| 7 | Documentación y release | README, versionado semántico, `main` ← `develop` |

## Licencia

MIT
