FROM python:3.10-slim

WORKDIR /code


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY frontend ./frontend

ENV GRADIO_SERVER_NAME="0.0.0.0"

# Expose Gradio's default port
EXPOSE 7860

# Run your demo script
CMD ["python", "./frontend/demo.py"]
