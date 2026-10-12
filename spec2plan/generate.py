import json
import os
import urllib.request
from typing import Any, List

from .models import EvidenceChunk, EvidenceReport, RetrievedEvidence, VerificationPlan

CATEGORIES = ["reset behavior", "handshake/backpressure", "ordering", "boundaries", "error handling"]


def evidence_report(query: str, results: List[RetrievedEvidence]) -> EvidenceReport:
    text = " ".join(item.chunk.text.lower() for item in results)
    categories = [category for category in CATEGORIES if any(
        word in text for word in category.replace("/", " ").split()
    )]
    return EvidenceReport(
        query=query,
        source_files=sorted({item.chunk.source_filename for item in results}),
        retrieved=results,
        evidence_categories=categories,
        categories_without_evidence=[category for category in CATEGORIES if category not in categories],
        note="Offline mode reports retrieved evidence only; no LLM call was made.",
    )


def _prompt(query: str, evidence: List[EvidenceChunk]) -> str:
    sources = "\n\n".join(
        f"[{chunk.id}] {chunk.source_filename}, page={chunk.page_number}, section={chunk.section_heading}\n{chunk.text}"
        for chunk in evidence
    )
    return f"""Generate a JSON object matching the VerificationPlan schema for query: {query}
Use only the evidence below. Every evidence_ids value must be one of the supplied IDs.
Separate specification facts from inferred assumptions in confidence_or_uncertainty.
Evidence:
{sources}"""


def generate_online(query: str, results: List[RetrievedEvidence]) -> VerificationPlan:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for online generation; use --offline.")
    payload = {
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        "messages": [{"role": "system", "content": "You produce source-grounded verification plans."},
                     {"role": "user", "content": _prompt(query, [item.chunk for item in results])}],
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }
    request = urllib.request.Request(
        os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body: Any = json.loads(response.read().decode("utf-8"))
    content = body["choices"][0]["message"]["content"]
    plan = VerificationPlan.model_validate(json.loads(content))
    valid_ids = {item.chunk.id for item in results}
    invalid = [evidence_id for item in plan.items for evidence_id in item.evidence_ids if evidence_id not in valid_ids]
    if invalid:
        raise ValueError(f"Generated citations do not map to retrieved evidence: {sorted(set(invalid))}")
    return plan
