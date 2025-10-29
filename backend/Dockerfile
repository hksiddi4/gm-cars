FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-k", "gevent", "-b", "unix:/tmp/gunicorn.sock", "start:app", "--preload"]
