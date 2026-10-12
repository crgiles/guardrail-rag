"""FastAPI application for the Guardrail RAG query service."""

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI

from guardrail_rag.generation.fake import FakeProvider
from guardrail_rag.generation.openrouter import OpenRouterProvider
from guardrail_rag.generation.provider import AnswerProvider
from guardrail_rag.ingestion.corpus import DocumentStore, load_corpus
from guardrail_rag.retrieval.simple import retrieve
from guardrail_rag.settings import Settings

from .schemas import Citation, QueryRequest, QueryResponse

_DEFAULT_CORPUS = Path(__file__).parents[3] / "data" / "synthetic"


def create_app(
    store: DocumentStore | None = None,
    provider: AnswerProvider | None = None,
) -> FastAPI:
    store = store or load_corpus(_DEFAULT_CORPUS)
    if provider is None:
        settings = Settings.from_env()
        provider = OpenRouterProvider() if settings.provider == "openrouter" else FakeProvider()
    app = FastAPI(title="Guardrail RAG", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/query", response_model=QueryResponse)
    def query(request: QueryRequest) -> QueryResponse:
        chunks = retrieve(list(store.chunks), request.question, request.role)
        result = provider.answer(request.question, chunks)
        citations = [
            Citation(
                document_id=chunk.document_id,
                chunk_id=chunk.chunk_id,
                title=chunk.document.title,
            )
            for chunk in chunks
        ]
        return QueryResponse(
            request_id=str(uuid4()),
            answer=result.answer,
            citations=citations,
            retrieved_count=len(chunks),
            refusal_reason=result.refusal_reason,
        )

    return app


app = create_app()
