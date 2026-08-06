FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN mkdir -p instance uploads/temp uploads/projects uploads/reports uploads/corrected uploads/diff \
    && useradd --create-home --uid 10001 sentrix \
    && chown -R sentrix:sentrix /app

USER sentrix
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl --fail --silent http://127.0.0.1:8000/ >/dev/null || exit 1

CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
