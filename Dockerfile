# Load base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1

# Create a non-root user
RUN addgroup --system app && adduser --system --ingroup app app

# Set working directory
WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files and to ensure stdout and stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and data
COPY --chown=app:app src ./src
COPY --chown=app:app tests ./tests
COPY --chown=app:app data/raw ./data/raw
RUN mkdir -p data/processed && chown -R app:app /app

# Set the user to run the application
USER app

# Run tests and start the application
CMD ["sh", "-c", "python -m pytest -q && python src/main.py"]
