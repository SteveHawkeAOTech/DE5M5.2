FROM python:3.13-slim

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app src ./src
COPY --chown=app:app tests ./tests
COPY --chown=app:app data/raw ./data/raw
RUN mkdir -p data/processed && chown -R app:app /app

USER app

CMD ["sh", "-c", "python -m pytest -q && python src/main.py"]
