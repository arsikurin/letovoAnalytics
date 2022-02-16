.PHONY: bot-dev api-dev bot-prod api-prod ping-api update-tokens run-dev okteto-deploy

BOT_SRC = ./app/main_bot.py
API_SRC = ./app/main_api.py
PINGER_SRC = ./app/pinger.py
HELPER_SRC = ./app/helper.py

bot-dev:
	python3 -X dev $(BOT_SRC)

api-dev:
	python3 -X dev $(API_SRC)

bot-prod:
	python3 $(BOT_SRC)

api-prod:
	python3 $(API_SRC)

ping-api:
	python3 $(PINGER_SRC)

update-tokens:
	python3 $(HELPER_SRC)

run-dev:
	docker compose up

# kubernetes
okteto-deploy:
	okteto stack deploy --build -f docker-compose.yaml
