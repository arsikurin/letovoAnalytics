.PHONY: bot-dev api-dev bot-prod api-prod ping-api update-tokens run-dev okteto-deploy

MAIN_SRC = ./app/main.py
ROOT_SRC = ./app/
OUTPUT_SRC = ./app/static/main.wasm

bot-dev:
	python3 -X dev $(MAIN_SRC) bot

api-dev:
	python3 -X dev $(MAIN_SRC) api

bot-prod:
	python3 $(MAIN_SRC) bot

api-prod:
	python3 $(MAIN_SRC) api

ping-api:
	python3 $(MAIN_SRC) ping

update-tokens:
	python3 $(MAIN_SRC) update

run-dev:
	docker compose up

build-wasm:
	env GOOS=js GOARCH=wasm go build -o $(OUTPUT_SRC) $(ROOT_SRC)

# kubernetes
okteto-deploy:
	okteto stack deploy --build -f docker-compose.yaml
