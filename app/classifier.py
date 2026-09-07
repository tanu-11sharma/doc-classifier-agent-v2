"""
Classifier agent.

Builds one TF-IDF "centroid" vector per category from the synthetic seed
documents, then classifies a new document by cosine similarity to each
centroid. If the top similarity score is below a confidence threshold, a
second, simpler keyword-rule agent is consulted as a fallback -- a small
example of the "agent escalates to another agent when unsure" pattern that
shows up in multi-agent orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.sample_documents import CATEGORY_SEED_DOCS

CONFIDENCE_THRESHOLD = 0.12

# Keyword fallback agent: simple, transparent, and cheap. Used only when the
# TF-IDF agent is not confident, mirroring how production systems often pair
# a statistical model with a deterministic rules engine as a safety net.
KEYWORD_RULES: dict[str, list[str]] = {
    "invoice": ["invoice", "amount due", "payment terms", "remit payment", "balance due"],
    "resume": ["resume", "curriculum vitae", "objective:", "work experience", "references available"],
    "contract": ["agreement", "contract", "non-disclosure", "statement of work", "effective date"],
    "support_ticket": ["ticket", "can't log in", "crashes", "bug", "priority: high", "reproduce"],
    "meeting_notes": ["attendees", "agenda", "action items", "standup", "retro"],
}


@dataclass
class ClassificationResult:
    category: str
    confidence: float
    method: str
    reasoning: list[str] = field(default_factory=list)


class DocumentClassifierAgent:
    """TF-IDF + cosine-similarity classifier over synthetic category centroids."""

    def __init__(self, seed_docs: dict[str, list[str]] | None = None) -> None:
        self.seed_docs = seed_docs or CATEGORY_SEED_DOCS
        self.categories = list(self.seed_docs.keys())

        corpus: list[str] = []
        self._category_doc_ranges: dict[str, tuple[int, int]] = {}
        for category, docs in self.seed_docs.items():
            start = len(corpus)
            corpus.extend(docs)
            self._category_doc_ranges[category] = (start, len(corpus))

        self.vectorizer = TfidfVectorizer(stop_words="english")
        self._corpus_matrix = self.vectorizer.fit_transform(corpus)

        # Centroid = mean TF-IDF vector of a category's seed documents.
        self._centroids = {
            category: np.asarray(
                self._corpus_matrix[start:end].mean(axis=0)
            ).reshape(1, -1)
            for category, (start, end) in self._category_doc_ranges.items()
        }

    def _tfidf_classify(self, text: str) -> ClassificationResult:
        vector = self.vectorizer.transform([text])
        scores = {
            category: float(cosine_similarity(vector, centroid)[0][0])
            for category, centroid in self._centroids.items()
        }
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        reasoning = [f"{cat}: similarity={score:.3f}" for cat, score in ranked]
        return ClassificationResult(
            category=best_category,
            confidence=best_score,
            method="tfidf_centroid",
            reasoning=reasoning,
        )

    def _keyword_classify(self, text: str) -> ClassificationResult | None:
        lowered = text.lower()
        hits: dict[str, int] = {}
        for category, keywords in KEYWORD_RULES.items():
            count = sum(1 for kw in keywords if kw in lowered)
            if count:
                hits[category] = count
        if not hits:
            return None
        best_category = max(hits, key=hits.get)
        total_hits = sum(hits.values())
        confidence = hits[best_category] / total_hits
        reasoning = [f"{cat}: {n} keyword hit(s)" for cat, n in sorted(hits.items(), key=lambda kv: kv[1], reverse=True)]
        return ClassificationResult(
            category=best_category,
            confidence=confidence,
            method="keyword_fallback",
            reasoning=reasoning,
        )

    def classify(self, text: str) -> ClassificationResult:
        if not text or not text.strip():
            return ClassificationResult(
                category="unclassified",
                confidence=0.0,
                method="empty_input",
                reasoning=["Input text was empty."],
            )

        primary = self._tfidf_classify(text)
        if primary.confidence >= CONFIDENCE_THRESHOLD:
            return primary

        fallback = self._keyword_classify(text)
        if fallback is not None and fallback.confidence > primary.confidence:
            fallback.reasoning = (
                [f"Primary TF-IDF agent was unconfident (best={primary.confidence:.3f}); escalated to keyword agent."]
                + fallback.reasoning
            )
            return fallback

        primary.reasoning = [
            f"Primary TF-IDF agent was unconfident (best={primary.confidence:.3f}); "
            "keyword fallback found no stronger signal, returning best-effort guess."
        ] + primary.reasoning
        return primary
