# syntax=docker/dockerfile:1

# Stage 1: Build dependencies
FROM python:3.13-slim AS builder

# Prevent .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Stage 2: Final image
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local /usr/local
ENV PATH=/usr/local/bin:$PATH

# Copy application code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose port and use entrypoint script
EXPOSE 8000
ENTRYPOINT ["/app/docker/entrypoint.sh"]