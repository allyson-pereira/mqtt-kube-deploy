FROM python:3.8-slim
WORKDIR /app
COPY config.json .
COPY dbpipe.py .
COPY requirements.txt .
RUN pip install --upgrade pip --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1
CMD ["python", "dbpipe.py"]