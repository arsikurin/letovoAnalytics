worker: python3 ./app/main.py
web: uvicorn app:app --workers 4 --host 0.0.0.0 --port=${PORT} --log-level debug