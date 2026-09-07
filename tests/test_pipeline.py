import json

from app.pipeline import DocumentRoutingPipeline


def test_pipeline_end_to_end(tmp_path):
    pipeline = DocumentRoutingPipeline()
    pipeline.router.log_path = tmp_path / "routing_log.jsonl"

    result = pipeline.run(
        "This agreement is entered into by and between the parties below. "
        "Non-disclosure agreement terms apply.",
        persist=True,
    )

    assert result.classification.category == "contract"
    assert result.routing.destination == "queue://legal/contract-review"
    assert pipeline.router.log_path.exists()

    lines = pipeline.router.log_path.read_text().strip().splitlines()
    assert len(lines) == 1
    logged = json.loads(lines[0])
    assert logged["category"] == "contract"


def test_pipeline_strips_whitespace():
    pipeline = DocumentRoutingPipeline()
    result = pipeline.run("   Invoice total amount due: $10.   ")
    assert result.extracted_text == "Invoice total amount due: $10."
