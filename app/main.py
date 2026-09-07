"""
FastAPI app exposing the document classification/routing pipeline.

Run locally:
    uvicorn app.main:app --reload

Then:
    curl -s -X POST http://127.0.0.1:8000/classify \
      -H "Content-Type: application/json" \
      -d '{"text": "Invoice #991 due on receipt. Total amount due: $500."}' | python3 -m json.tool
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.pipeline import DocumentRoutingPipeline
from app.sample_documents import CATEGORY_SEED_DOCS

app = FastAPI(
    title="doc-classifier-agent-v2",
    description=(
        "Demo document classification/routing agent. Classifies short text "
        "documents into categories (invoice, resume, contract, support "
        "ticket, meeting notes) and simulates routing them to a destination "
        "queue. All data is synthetic; nothing here contacts a real system."
    ),
    version="0.1.0",
)

pipeline = DocumentRoutingPipeline()


class ClassifyRequest(BaseModel):
    text: str = Field(..., description="Raw document text to classify.")
    persist: bool = Field(
        False,
        description="If true, append the routing decision to data/routing_log.jsonl.",
    )


class ClassifyResponse(BaseModel):
    extracted_text: str
    category: str
    confidence: float
    method: str
    destination: str
    reasoning: list[str]


@app.get("/")
def root() -> dict:
    return {
        "service": "doc-classifier-agent-v2",
        "categories": list(CATEGORY_SEED_DOCS.keys()),
        "endpoints": ["/classify", "/categories", "/healthz"],
    }


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/categories")
def categories() -> dict:
    return {"categories": list(CATEGORY_SEED_DOCS.keys())}


@app.post("/classify", response_model=ClassifyResponse)
def classify(request: ClassifyRequest) -> ClassifyResponse:
    result = pipeline.run(request.text, persist=request.persist)
    return ClassifyResponse(
        extracted_text=result.extracted_text,
        category=result.classification.category,
        confidence=round(result.classification.confidence, 4),
        method=result.classification.method,
        destination=result.routing.destination,
        reasoning=result.classification.reasoning,
    )
