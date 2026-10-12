FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GUARDRAIL_RAG_PROVIDER=fake

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data

RUN python -m pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "guardrail_rag.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
