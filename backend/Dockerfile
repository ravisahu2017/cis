FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies including OpenCV requirements and Poppler for PDF processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libxtst6 \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8001

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Production target
FROM base as prod
# Run the application
CMD ["python", "fastapi_app.py"]

# Debug target
FROM base as debug
# Install debugpy
RUN pip install debugpy

# Debug environment
ENV DEBUG=true

# Expose ports
EXPOSE 8001 5678

# Debug command
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "fastapi_app.py"]
