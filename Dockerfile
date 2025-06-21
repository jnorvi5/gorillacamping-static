<<<<<<< HEAD
# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

# Set working directory
WORKDIR /app

# --- Builder stage: install dependencies in a venv ---
FROM base AS builder

# Install build dependencies (if any needed for pip packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt first for better cache usage
COPY --link requirements.txt ./

# Create venv and install dependencies using pip cache
RUN python -m venv .venv \
    && .venv/bin/pip install --upgrade pip \
    && --mount=type=cache,target=/root/.cache/pip \
       .venv/bin/pip install -r requirements.txt

# Copy the rest of the application code (excluding venv, .git, etc.)
COPY --link . .

# --- Final stage ---
FROM base AS final

# Create a non-root user
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

WORKDIR /app

# Copy app source and venv from builder
COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the port Flask runs on (default 5000)
EXPOSE 5000

# Switch to non-root user
USER appuser

# Entrypoint: run the Flask app
CMD ["python", "app.py"]
=======
# Use a lightweight base image with Python 3
FROM python:3.10-slim

# Create a directory for your app
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask code into the container
COPY . .

# Expose Flask’s port (5000 if using Gunicorn)
EXPOSE 5000

# Start the server with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
>>>>>>> df671eb924487af6896b18f97f50cf2a8c194cb6
