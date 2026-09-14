#!/bin/sh
set -e

alembic upgrade head
python bin/run.py &
exec uvicorn order_service.fastapi:app --host 0.0.0.0 --port 8000
