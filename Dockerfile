FROM ghcr.io/astral-sh/uv:python3.12-alpine AS base
LABEL org.opencontainers.image.authors="jpl.hanna@gmail.com"
WORKDIR /app/
COPY . /app/

FROM base AS install-uv-packages

ENV PATH="/app/.venv/bin:$PATH" \
    UV_FROZEN=True \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Install python dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Install application into container
ENV PYTHONPATH "$PYTHONPATH:/app/"

# Make Logs directory
RUN mkdir /app/logs
RUN touch /app/logs/discord.log

FROM install-uv-packages AS install-dev
RUN uv sync --frozen --no-install-project --only-dev
