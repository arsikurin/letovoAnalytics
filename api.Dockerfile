FROM python:3.10.0-bullseye

WORKDIR /app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
RUN $HOME/.local/bin/poetry export -o requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--workers 4", "--host 0.0.0.0", "--port=${PORT}", "--log-level debug"]
