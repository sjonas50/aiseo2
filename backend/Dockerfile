FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
COPY requirements.txt ./main-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r main-requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY *.py ./
COPY questions.txt ./

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "backend/app.py"]