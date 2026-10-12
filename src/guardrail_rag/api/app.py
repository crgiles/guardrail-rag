"""FastAPI application for the Guardrail RAG query service."""

import logging
import time
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from guardrail_rag.generation.fake import FakeProvider
from guardrail_rag.generation.openrouter import OpenRouterError, OpenRouterProvider
from guardrail_rag.generation.provider import AnswerProvider
from guardrail_rag.ingestion.corpus import DocumentStore, load_corpus
from guardrail_rag.observability.logging import configure_logging, request_fields
from guardrail_rag.retrieval.simple import retrieve
from guardrail_rag.settings import Settings

from .schemas import Citation, QueryRequest, QueryResponse

logger = logging.getLogger("guardrail_rag.api")

_DEFAULT_CORPUS = Path(__file__).parents[3] / "data" / "synthetic"


def create_app(
    store: DocumentStore | None = None,
    provider: AnswerProvider | None = None,
) -> FastAPI:
    """Create the FastAPI application with injectable store and provider."""
    settings = Settings.from_env()
    corpus_path = Path(settings.corpus_dir)
    if not corpus_path.is_absolute():
        # Resolve relative paths from the repository root, not the process
        # working directory, so launching the service from elsewhere is safe.
        corpus_path = _DEFAULT_CORPUS.parent.parent / corpus_path
    store = store or load_corpus(corpus_path)
    if provider is None:
        provider = OpenRouterProvider() if settings.provider == "openrouter" else FakeProvider()
    configure_logging()
    factory_app = FastAPI(title="Guardrail RAG", version="0.1.0")

    @factory_app.middleware("http")
    async def request_logging(request: Request, call_next):
        """Attach a correlation ID and log safe request metadata."""
        request_id = request.headers.get("x-request-id", str(uuid4()))
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:  # pylint: disable=broad-exception-caught
            fields = request_fields(
                request_id, request.method, request.url.path, 500, started
            )
            logger.exception("request_failed", extra={"fields": fields})
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id},
            )
        response.headers["x-request-id"] = request_id
        fields = request_fields(
            request_id, request.method, request.url.path, response.status_code, started
        )
        logger.info("request_completed", extra={"fields": fields})
        return response

    @factory_app.get("/health")
    def health() -> dict[str, str]:
        """Report service health."""
        return {"status": "ok"}

    @factory_app.post("/query", response_model=QueryResponse)
    def query(request: QueryRequest) -> QueryResponse:
        """Retrieve authorized evidence and generate a grounded response."""
        # Retrieval performs authorization before ranking; the provider only
        # receives this already-filtered evidence set.
        chunks = retrieve(list(store.chunks), request.question, request.role)
        try:
            result = provider.answer(request.question, chunks)
        except OpenRouterError as exc:
            logger.warning(
                "provider_failed",
                extra={"fields": {"provider_error": type(exc).__name__}},
            )
            return QueryResponse(
                request_id=str(uuid4()),
                answer="The answer provider is temporarily unavailable.",
                citations=[],
                retrieved_count=0,
                refusal_reason="provider_unavailable",
            )
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

    return factory_app


app = create_app()
