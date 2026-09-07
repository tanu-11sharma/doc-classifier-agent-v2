"""
Orchestration layer that chains the extractor, classifier, and router
"agents" into a single pipeline -- a small illustration of multi-agent
orchestration without needing a heavyweight framework.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from app.classifier import ClassificationResult, DocumentClassifierAgent
from app.router import RoutingAgent, RoutingDecision


def extract(raw_text: str) -> str:
    """Extractor agent: trivial normalization step.

    In a real system this is where OCR, PDF parsing, or HTML stripping
    would happen. Here it just trims whitespace, but it's kept as its own
    pipeline stage so the extractor can be swapped out independently of the
    classifier and router.
    """
    return raw_text.strip()


@dataclass
class PipelineResult:
    extracted_text: str
    classification: ClassificationResult
    routing: RoutingDecision

    def to_dict(self) -> dict:
        return {
            "extracted_text": self.extracted_text,
            "classification": asdict(self.classification),
            "routing": asdict(self.routing),
        }


class DocumentRoutingPipeline:
    """extractor -> classifier agent -> router agent"""

    def __init__(self) -> None:
        self.classifier = DocumentClassifierAgent()
        self.router = RoutingAgent()

    def run(self, raw_text: str, *, persist: bool = False) -> PipelineResult:
        extracted = extract(raw_text)
        classification = self.classifier.classify(extracted)
        routing = self.router.route(classification, persist=persist)
        return PipelineResult(
            extracted_text=extracted,
            classification=classification,
            routing=routing,
        )
