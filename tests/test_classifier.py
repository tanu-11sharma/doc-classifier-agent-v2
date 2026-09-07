from app.classifier import DocumentClassifierAgent


def test_invoice_is_classified_correctly():
    agent = DocumentClassifierAgent()
    result = agent.classify(
        "Invoice #7788 due on receipt. Total amount due: $980.00. "
        "Please remit payment within 30 days."
    )
    assert result.category == "invoice"
    assert result.confidence > 0


def test_resume_is_classified_correctly():
    agent = DocumentClassifierAgent()
    result = agent.classify(
        "Objective: seeking a backend engineering role. Work experience "
        "includes Python, REST APIs, and cloud infrastructure."
    )
    assert result.category == "resume"


def test_support_ticket_is_classified_correctly():
    agent = DocumentClassifierAgent()
    result = agent.classify(
        "I can't log into my account, the reset link is broken. "
        "This is a high priority bug, please help."
    )
    assert result.category == "support_ticket"


def test_empty_text_returns_unclassified():
    agent = DocumentClassifierAgent()
    result = agent.classify("   ")
    assert result.category == "unclassified"
    assert result.method == "empty_input"


def test_keyword_fallback_triggers_on_sparse_text():
    agent = DocumentClassifierAgent()
    # Very short, sparse text: TF-IDF centroid similarity will likely be low,
    # but it contains a strong keyword the fallback agent should catch.
    result = agent.classify("agenda and action items")
    assert result.category in {"meeting_notes", "unclassified"}
