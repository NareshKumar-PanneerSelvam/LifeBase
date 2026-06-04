# ==============================================================================
# Build Stage - Install dependencies using UV in a python-slim base
# ==============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install UV by copying from the official image
COPY --from=ghcr.io/astral-sh/uv:0.6.1 /uv /uvx /bin/

# Enable Python bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency specifications
COPY pyproject.toml /app/

# Compile pyproject.toml dependencies to a standard requirements.txt
# and install them into system python packages using mount cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt

# ==============================================================================
# Production Stage - Minimal slim runner
# ==============================================================================
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy installed site-packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy code bases and configs
COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/
COPY .env.example /app/.env

EXPOSE 8000

# Keep stdout/stderr streams unbuffered
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
