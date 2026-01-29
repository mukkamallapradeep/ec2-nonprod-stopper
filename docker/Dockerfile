FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

ENV PYTHONUNBUFFERED=1
EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.web:app"]
