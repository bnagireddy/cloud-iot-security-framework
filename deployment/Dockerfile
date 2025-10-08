# Cloud-Native IoT Security Framework
# Multi-stage Docker build for production deployment

# Stage 1: Base Python environment
FROM python:3.11.4-slim AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Application
FROM base AS application

# Copy source code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create directories for data and models
RUN mkdir -p data models results logs figures

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 1883 5683 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "scripts/run_experiments.py"]

# Stage 3: Development (includes dev tools)
FROM application AS development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest==7.4.0 \
    pytest-cov==4.1.0 \
    black==23.7.0 \
    flake8==6.0.0 \
    mypy==1.4.1 \
    ipython==8.14.0

# Default to bash for interactive development
CMD ["/bin/bash"]
