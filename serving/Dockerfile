FROM python:3.10-slim

WORKDIR /app

COPY app.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "app:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "10", \
     "--bind", "0.0.0.0:8000", \
     "--reload"] 