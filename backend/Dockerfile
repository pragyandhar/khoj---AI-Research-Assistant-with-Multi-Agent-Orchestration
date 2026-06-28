# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency configuration files first to utilize Docker layer cache
COPY pyproject.toml uv.lock ./

# Sync dependencies (frozen lockfile, exclude development packages)
RUN uv sync --frozen --no-dev

# Stage 2: Final runtime image
FROM python:3.11-slim

WORKDIR /app

# Copy the built virtual environment from the builder stage
COPY --from=builder /app/.venv ./.venv

# Copy the application code
COPY ./app ./app

# Add virtual environment to PATH so python/uvicorn are picked up automatically
ENV PATH="/app/.venv/bin:$PATH"

# Start the application using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]