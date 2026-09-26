# JAN-SARTHI AI Dockerfile
# Production-ready container for Google Cloud Run / Container Registry
# Adheres to non-root execution and zero-secret hardcoding

FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV DEMO_MODE=true

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and datasets
COPY jan_sarthi_agent/ jan_sarthi_agent/
COPY app/ app/
COPY data/ data/
COPY pytest.ini .

# Create non-root user for security compliance
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

# Health-friendly startup for Google Cloud Run
CMD ["sh", "-c", "streamlit run app/streamlit_app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
