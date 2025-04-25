.PHONY: up down build migrate logs start

up:
	docker-compose up --build --force-recreate --remove-orphans -d

down:
	docker-compose down --remove-orphans

build:
	docker-compose build --no-cache --pull

migrate:
	docker-compose exec backend alembic upgrade head

logs:
	docker-compose logs -f --tail=100

clear:
	docker-compose down -v --remove-orphans

start: up migrate logs
