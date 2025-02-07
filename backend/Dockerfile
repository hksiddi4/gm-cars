FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "start.py"]
