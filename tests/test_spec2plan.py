import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from spec2plan.generate import generate_online
from spec2plan.ingest import ingest_document
from spec2plan.models import VerificationPlan
from spec2plan.retrieve import retrieve

ROOT = Path(__file__).parents[1]


def test_markdown_ingestion_preserves_metadata_and_stable_ids(tmp_path):
    path = tmp_path / "protocol.md"
    path.write_text("# Section A\n\nA requirement.\n\n## Section B\n\nAnother requirement.", encoding="utf-8")
    first = ingest_document(path)
    second = ingest_document(path)
    assert [item.id for item in first] == [item.id for item in second]
    assert first[0].source_filename == "protocol.md"
    assert first[0].section_heading == "Section A"


def test_retrieval_ranks_handshake_evidence():
    chunks = ingest_document(ROOT / "examples" / "sample_protocol_spec.md")
    results = retrieve(chunks, "backpressure payload stability", top_k=2)
    assert results
    assert "payload" in results[0].chunk.text.lower()
    assert results[0].chunk.source_filename == "sample_protocol_spec.md"


def test_invalid_citations_are_rejected(monkeypatch):
    class FakeResponse:
        def read(self):
            item = {
                "requirement_id": "R1", "requirement_statement": "x",
                "supporting_quotation": "x", "verification_objective": "x",
                "test_scenario": "x", "expected_behavior": "x", "relevant_signals": ["x"],
                "candidate_sva": "assert property (x);", "clock_reset_sampling_assumptions": "x",
                "confidence_or_uncertainty": "x", "evidence_ids": ["not-real"], "category": "ordering",
            }
            return json.dumps({"choices": [{"message": {"content": json.dumps({
                "query": "x", "items": [item], "uncovered_categories": []
            })}}]}).encode()
        def __enter__(self): return self
        def __exit__(self, *args): return None

    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: FakeResponse())
    chunks = ingest_document(ROOT / "examples" / "sample_protocol_spec.md")
    with pytest.raises(ValueError, match="citations"):
        generate_online("handshake", retrieve(chunks, "handshake"))


def test_schema_rejects_missing_required_fields():
    with pytest.raises(ValidationError):
        VerificationPlan.model_validate({"query": "x", "items": [{}], "uncovered_categories": []})


def test_offline_cli(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "run_agent.py"), "--spec", str(ROOT / "examples" / "sample_protocol_spec.md"),
         "--query", "backpressure and payload stability", "--outdir", str(tmp_path), "--offline"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    assert "offline evidence report" in result.stdout
    report = json.loads((tmp_path / "evidence_report.json").read_text(encoding="utf-8"))
    assert report["retrieved"]
    assert report["retrieved"][0]["chunk"]["section_heading"] == "Handshake and payload stability"
