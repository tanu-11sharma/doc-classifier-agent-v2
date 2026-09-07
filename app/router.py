"""
Router agent.

Takes a classification result and decides where the document *would* be
routed. This is a simulation: the "destination" is just a label plus an
in-memory/append-only JSON-lines log written inside the repo's own data
directory. No real external system (email, ticketing tool, file share) is
ever contacted.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from app.classifier import ClassificationResult

DESTINATIONS: dict[str, str] = {
    "invoice": "queue://finance/accounts-payable",
    "resume": "queue://recruiting/inbound-candidates",
    "contract": "queue://legal/contract-review",
    "support_ticket": "queue://support/triage",
    "meeting_notes": "queue://knowledge-base/meeting-archive",
    "unclassified": "queue://manual-review/needs-human",
}

LOG_PATH = Path(__file__).resolve().parent.parent / "data" / "routing_log.jsonl"


@dataclass
class RoutingDecision:
    category: str
    confidence: float
    method: str
    destination: str
    reasoning: list[str]
    routed_at: float


class RoutingAgent:
    """Decides a (simulated) destination queue for a classified document."""

    def __init__(self, log_path: Path = LOG_PATH) -> None:
        self.log_path = log_path

    def route(self, result: ClassificationResult, *, persist: bool = False) -> RoutingDecision:
        destination = DESTINATIONS.get(result.category, DESTINATIONS["unclassified"])
        decision = RoutingDecision(
            category=result.category,
            confidence=result.confidence,
            method=result.method,
            destination=destination,
            reasoning=result.reasoning,
            routed_at=time.time(),
        )
        if persist:
            self._append_log(decision)
        return decision

    def _append_log(self, decision: RoutingDecision) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(decision)) + "\n")
