FROM python:3.10.4 as base
MAINTAINER JP Hanna "jpl.hanna@gmail.com"
WORKDIR /app/
COPY . /app/

FROM base as install-poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.2.0b3
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN apt-get update && apt-get install -y --no-install-recommends gcc
ENV PATH "/root/.local/bin:$PATH"

# Install python dependencies in /.venv
RUN poetry install --no-root --no-ansi --no-interaction --only=main

# Install application into container
ENV PYTHONPATH "{$PYTHONPATH}:/app/"

FROM install-poetry as install-dev
RUN poetry install --no-root --no-ansi --no-interaction --only=dev
