FROM python:3.10.2-bullseye AS dev

WORKDIR /app-data

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
RUN "${HOME}"/.local/bin/poetry config virtualenvs.create false

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN "${HOME}"/.local/bin/poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD ["make", "bot-dev"]


FROM python:3.10.2-bullseye AS prod

WORKDIR /app-data

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
RUN "${HOME}"/.local/bin/poetry config virtualenvs.create false

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock
RUN "${HOME}"/.local/bin/poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD ["make", "bot-prod"]