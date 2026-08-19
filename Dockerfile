FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY docker.requirements .

RUN pip install --no-cache-dir -r docker.requirements

COPY . .

RUN alembic upgrade head

CMD ["python", "-m", "main.py"]