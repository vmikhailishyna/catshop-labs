# Basic Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
ENV COUNTER_FILE=/app/data/visits.txt \
    PYTHONUNBUFFERED=1

EXPOSE 8080
CMD ["python", "app.py"]