FROM python:3.10-slim

WORKDIR /code

# Install dependencies
RUN apt-get update && \
    apt-get install -y curl netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY workflow ./workflow

RUN chmod +x ./workflow/start.sh


CMD ["bash", "./workflow/start.sh"]
