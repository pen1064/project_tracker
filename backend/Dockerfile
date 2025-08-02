FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install curl and netcat (for health checks and wait-for-db)
RUN apt-get update && \
    apt-get install -y curl netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ../requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code (including start.sh)
COPY backend ./backend

# Ensure start.sh is executable
RUN chmod +x ./backend/start.sh

# Default command
CMD ["bash", "./backend/start.sh"]
