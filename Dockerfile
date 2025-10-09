# Base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# --- Step 1: Install system dependencies for pyodbc ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        g++ \
        unixodbc-dev \
        curl \
        libssl-dev \
        && rm -rf /var/lib/apt/lists/*

# --- Step 2: Copy project files ---
COPY . /app/

# --- Step 3: Upgrade pip and install Python dependencies ---
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt

# --- Step 4: Expose port (Render default is 5000) ---
EXPOSE 5000

# --- Step 5: Set environment variables defaults ---
ENV PORT=5000
ENV FLASK_ENV=production

# --- Step 6: Run the app using Gunicorn for production ---
# 'main:app' because your Flask app instance is 'app' in main.py
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
