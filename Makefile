.PHONY: help infra-up infra-down infra-logs topic-create backend-install backend-run test lint

# Muestra todos los comandos disponibles
help:
	@echo "StreamSocial — Comandos disponibles:"
	@echo ""
	@echo "  Infraestructura:"
	@echo "    make infra-up        Levanta Kafka, Zookeeper y Kafka UI"
	@echo "    make infra-down      Detiene y elimina los contenedores"
	@echo "    make infra-logs      Muestra logs de los contenedores"
	@echo "    make topic-create    Crea el topic streamsocial-events"
	@echo ""
	@echo "  Backend:"
	@echo "    make backend-install Instala dependencias Python"
	@echo "    make backend-run     Inicia el servidor FastAPI"
	@echo ""
	@echo "  Calidad:"
	@echo "    make test            Corre todos los tests"
	@echo "    make lint            Corre el linter (ruff)"

infra-up:
	docker compose up -d
	@echo "Kafka UI disponible en http://localhost:8080"

infra-down:
	docker compose down -v

infra-logs:
	docker compose logs -f

topic-create:
	docker exec streamsocial-kafka kafka-topics \
		--bootstrap-server localhost:9092 \
		--create --if-not-exists \
		--topic streamsocial-events \
		--partitions 3 \
		--replication-factor 1

backend-install:
	cd backend && pip install -r requirements.txt

backend-run:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

test:
	cd backend && pytest tests/ -v

lint:
	cd backend && ruff check .
