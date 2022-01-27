bot-dev:
	python3 -X dev ./app/main_bot.py

api-dev:
	python3 -X dev ./app/main_api.py

bot-prod:
	python3 ./app/main_bot.py

api-prod:
	python3 ./app/main_api.py

ping-api:
	python3 ./app/pinger.py

update-tokens:
	python3 ./app/helper.py

run-dev:
	docker compose up

# kubernetes
okteto-deploy:
	okteto stack deploy --build -f docker-compose.yaml
