FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN uv sync --frozen --no-dev

COPY alembic.ini ./
COPY alembic ./alembic
COPY bin ./bin

EXPOSE 8000

RUN chmod +x bin/start.sh

CMD ["bin/start.sh"]
