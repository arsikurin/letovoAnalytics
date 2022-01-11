bot-dev:
	python3 -X dev ./app/main_bot.py

api-dev:
	python3 -X dev ./app/main_api.py

bot-prod:
	python3 ./app/main_bot.py

api-prod:
	python3 ./app/main_api.py
