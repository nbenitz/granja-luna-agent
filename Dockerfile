FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY runtime/requirements.txt /app/runtime/requirements.txt
RUN pip install --no-cache-dir -r /app/runtime/requirements.txt
COPY runtime /app/runtime

EXPOSE 8011
CMD ["uvicorn", "runtime.src.web.app:app", "--host", "0.0.0.0", "--port", "8011"]
