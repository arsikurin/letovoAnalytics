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

# for ARM
bot-dev-arm:
	arch -x86_64 python3 -X dev ./app/main_bot.py

api-dev-arm:
	arch -x86_64 python3 -X dev ./app/main_api.py

bot-prod-arm:
	arch -x86_64 python3 ./app/main_bot.py

api-prod-arm:
	arch -x86_64 python3 ./app/main_api.py

ping-api-arm:
	arch -x86_64 python3 ./app/pinger.py
