FROM ghcr.io/astral-sh/uv:python3.12-alpine AS base
LABEL org.opencontainers.image.authors="jpl.hanna@gmail.com"
WORKDIR /app/
COPY . /app/

FROM base AS install-uv-packages

ENV PATH="/app/.venv/bin:$PATH" \
    UV_FROZEN=True \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/opt/uv-cache/

# Install python dependencies
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --no-install-project --no-dev

# Install application into container
ENV PYTHONPATH "$PYTHONPATH:/app/"

# Make Logs directory
RUN mkdir /app/logs
RUN touch /app/logs/discord.log

FROM install-uv-packages AS install-dev
RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --no-install-project --only-dev
