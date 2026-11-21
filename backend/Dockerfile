FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-k", "gevent", "-b", "0.0.0.0:5000", "--keep-alive", "15", "--timeout", "120", "start:app", "--preload"]
