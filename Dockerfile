FROM python:3.13-slim

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY data/raw ./data/raw

USER app

CMD ["python", "src/main.py"]
