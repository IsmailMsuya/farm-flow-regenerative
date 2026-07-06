FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY farmflow ./farmflow
COPY app ./app
COPY mcp_servers ./mcp_servers
COPY frontend ./frontend
COPY contracts ./contracts
COPY data ./data

RUN pip install --no-cache-dir .

EXPOSE 8080

CMD ["python", "-m", "farmflow.api"]

