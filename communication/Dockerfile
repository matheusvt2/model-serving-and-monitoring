FROM python:3.10-slim

WORKDIR /app

COPY streaming.py ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python", "streaming.py"] 