FROM python:3.11.4-slim as base
MAINTAINER JP Hanna "jpl.hanna@gmail.com"
WORKDIR /app/
COPY . /app/

FROM base as install-poetry

# Set env variables
ENV PIPX_BIN_DIR="/opt/pipx" \
    POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_CACHE_DIR="/opt/poetry" \
    POETRY_VERSION=1.7.0 \
    PATH="/root/.local/share/pipx/venvs/poetry/bin:$PATH"
ENV PATH="$POETRY_VIRTUALENVS_PATH/bin:$PIPX_BIN_DIR:$PATH"

# Install poetry
RUN pip install --upgrade pip \
    && pip install pipx \
    && pipx install poetry==$POETRY_VERSION
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies
RUN poetry install --no-root --no-ansi --no-interaction --only=main --no-directory

# Install application into container
ENV PYTHONPATH "$PYTHONPATH:/app/"

FROM install-poetry as install-dev
RUN poetry install --no-root --no-ansi --no-interaction --only=dev --no-directory
