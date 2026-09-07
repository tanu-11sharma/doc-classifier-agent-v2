# doc-classifier-agent-v2

> **Why "v2"?** An earlier repo in this build series, [`doc-classifier-agent`](https://github.com/tanu-11sharma/doc-classifier-agent), already covers a pure rule-based / keyword-scoring approach to document classification. This v2 takes a different technical angle on the same problem: a TF-IDF + cosine-similarity classifier agent that only falls back to keyword rules when it isn't confident, plus a separate router agent and a small extractor -> classifier -> router pipeline.

A small, self-contained demo of a **document classification and routing agent**: it reads a short piece of text, classifies it into a category (invoice, resume, contract, support ticket, meeting notes), and decides which downstream queue it *would* be routed to — all using synthetic, hand-written sample data.

## What it does

The pipeline runs three stages, each modeled as its own small "agent":

1. **Extractor** — normalizes raw input text (a stand-in for OCR/PDF-parsing/HTML-stripping in a real system).
2. **Classifier agent** — builds a TF-IDF "centroid" vector for each category from a handful of synthetic seed documents, then classifies new text by cosine similarity to those centroids. If the top match is below a confidence threshold, it escalates to a **keyword fallback agent** — a simple rules engine used as a safety net.
3. **Router agent** — maps the winning category to a simulated destination queue (e.g. `queue://finance/accounts-payable`) and optionally appends the decision to an append-only local log file.

## Why this is relevant

Document classification/routing is one of the most common real-world "boring but valuable" agentic AI patterns — it shows up in inbox triage, support ticket routing, and back-office automation. This demo illustrates a lightweight multi-agent orchestration pattern (extractor → classifier → router, with an agent-escalates-to-agent fallback) without needing a heavyweight framework or any external API keys.

**This is a demo/simulation only.** No real emails, tickets, or files are read or moved; "routing" only ever means writing a line to a local JSON-lines log inside this repo, and the seed documents are all invented text, not real correspondence.

## Project structure

```
app/
  main.py               FastAPI app (HTTP interface)
  pipeline.py            Orchestrates extractor -> classifier -> router
  classifier.py          TF-IDF classifier agent + keyword fallback agent
  router.py              Routing agent (simulated destinations + local log)
  sample_documents.py    Synthetic seed documents per category
tests/
  test_classifier.py
  test_pipeline.py
  test_api.py
data/
  routing_log.jsonl      (created at runtime if persist=true; gitignored)
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Example usage

```bash
curl -s -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Invoice #991 due on receipt. Total amount due: $500."}' | python3 -m json.tool
```

Example response:

```json
{
  "extracted_text": "Invoice #991 due on receipt. Total amount due: $500.",
  "category": "invoice",
  "confidence": 0.4123,
  "method": "tfidf_centroid",
  "destination": "queue://finance/accounts-payable",
  "reasoning": ["invoice: similarity=0.412", "contract: similarity=0.091", "..."]
}
```

Or use it as a plain Python library without the HTTP layer:

```python
from app.pipeline import DocumentRoutingPipeline

pipeline = DocumentRoutingPipeline()
result = pipeline.run("Attendees: product and design. Agenda: Q3 roadmap.")
print(result.classification.category)  # "meeting_notes"
```

## Test

```bash
pip install -r requirements.txt
pytest -v
```

## Docker

```bash
docker build -t doc-classifier-agent-v2 .
docker run -p 8000:8000 doc-classifier-agent-v2
```

## Categories supported

`invoice`, `resume`, `contract`, `support_ticket`, `meeting_notes` (plus `unclassified` as a catch-all).

## Disclaimer

This project is a technical demo built with synthetic data. It does not connect to any real email inbox, ticketing system, or file store, and its outputs should not be relied on for real business, financial, legal, or hiring decisions.
