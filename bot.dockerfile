FROM python:3.11-bullseye AS base

WORKDIR /app-data

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN curl -sSL https://install.python-poetry.org | python3 -
RUN "${HOME}"/.local/bin/poetry config virtualenvs.create false

COPY pyproject.toml ./
COPY poetry.lock ./
RUN "${HOME}"/.local/bin/poetry install --no-dev --no-interaction --no-ansi --no-cache

COPY . .


FROM base AS dev

RUN echo "dev version"

CMD ["make", "bot-dev"]


FROM base AS prod

RUN echo "prod version"

CMD ["make", "bot-prod"]