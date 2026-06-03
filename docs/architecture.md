# Arquitectura de StreamSocial

## Decisión: ¿Por qué Kafka y no RabbitMQ o Redis Pub/Sub?

| Criterio | Kafka | RabbitMQ | Redis Pub/Sub |
|---|---|---|---|
| Retención de mensajes | Sí (configurable) | No (se elimina al consumir) | No |
| Replay de eventos | Sí | No | No |
| Throughput | Muy alto | Alto | Alto |
| Ordenamiento | Por partición | Por cola | No garantizado |
| Ideal para | Event streaming, logs, analytics | Colas de trabajo, RPC | Notificaciones simples |

**Elegimos Kafka porque:** en una red social real necesitamos poder "rebobinar" el stream de eventos (ej: un nuevo servicio de recomendaciones necesita procesar todos los eventos históricos). Kafka retiene los mensajes según su política de retención configurada.

## Modelo de Particiones

El topic `streamsocial-events` tiene **3 particiones**. La clave de partición es el `user_id`:

```
Partición 0 ← eventos del user_001, user_004, user_007...
Partición 1 ← eventos del user_002, user_005, user_008...
Partición 2 ← eventos del user_003, user_006, user_009...
```

**Por qué usar user_id como clave:** garantiza que todos los eventos de un mismo usuario lleguen en orden cronológico al mismo consumer, lo cual es crítico para reconstruir el historial de un usuario.

## Flujo de Datos

```
POST /events/user/register
         │
         ▼
   FastAPI Handler
         │
         ▼
StreamSocialEventProducer
   serialize → JSON
   key → user_id
         │
         ▼
  Kafka Broker
  Topic: streamsocial-events
  Particiones: 3
         │
         ▼
StreamSocialEventConsumer
   deserialize ← JSON
   dispatch → handlers
         │
         ▼
  eventos_procesados[]  ← GET /events/recent
         │
         ▼
   Dashboard React
   polling cada 2s
```

## Variables de Entorno

Todas las configuraciones sensibles o que cambian entre entornos van en `.env` (nunca en el código). Ver `.env.example` para la lista completa.
