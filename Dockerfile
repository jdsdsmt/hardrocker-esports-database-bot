FROM python:3.14-slim

# Keep Python output unbuffered so logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir discord-py dotenv

COPY main.py ./
COPY bot ./bot

CMD ["python", "main.py"]

