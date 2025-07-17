# Base image with Python 3.11
FROM python:3.11-slim

# Install Node.js for the frontend build
RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY frontend ./frontend

# Build the React frontend
RUN cd frontend && npm install && npm run build

# Copy start script
COPY docker/start.sh ./start.sh
RUN chmod +x start.sh

EXPOSE 5000
EXPOSE 5173

# Start both backend and frontend
CMD ["./start.sh"]
