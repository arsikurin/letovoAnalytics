worker: python3 ./app/main_bot.py
web: uvicorn main_api:app --app-dir "./app/" --workers 4 --host 0.0.0.0 --port=${PORT} --loop uvloop
web: python3 ./app/main_api.py ${PORT}