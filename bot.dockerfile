FROM python:3.10.2-bullseye as prod

WORKDIR /app-data

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
RUN ${HOME}/.local/bin/poetry config virtualenvs.create false

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN ${HOME}/.local/bin/poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD ["make", "bot-prod"]


FROM python:3.10.1-bullseye as dev

WORKDIR /app-data

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
RUN ${HOME}/.local/bin/poetry config virtualenvs.create false

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN ${HOME}/.local/bin/poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD ["make", "bot-dev"]