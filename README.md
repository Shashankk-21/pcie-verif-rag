# Spec2Plan

Spec2Plan is an independently implemented MVP that turns protocol-specification
passages into source-grounded verification evidence and, when configured with an
LLM, structured verification-plan candidates and SystemVerilog Assertions (SVA).
The included protocol document is synthetic and educational; it is not PCIe,
AXI, or any other official specification.

## Features

- Ingests Markdown, plain text, and PDF files.
- Preserves filename, PDF page number, section heading, and a stable chunk ID.
- Retrieves with a dependency-light hybrid ranker: lexical overlap plus TF-IDF
  cosine similarity. Results are deduplicated and retain their source metadata.
- Offline mode produces a JSON and readable Markdown evidence report without
  calling an LLM or requiring credentials.
- Online mode uses the OpenAI-compatible Chat Completions API and validates the
  returned plan with Pydantic. Citations that do not refer to retrieved chunks
  are rejected.
- Reports evidence found for reset behavior, handshake/backpressure, ordering,
  boundaries, and error handling, as well as categories not supported by the
  supplied evidence.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The tested code requires Python 3.10 or newer. PDF parsing uses `pypdf`.

## CLI

Run the offline demonstration:

```powershell
python run_agent.py --spec examples/sample_protocol_spec.md `
  --query "backpressure and payload stability" --outdir output --offline
```

This writes `output/evidence_report.json` and `output/evidence_report.md`.
Offline mode intentionally does not generate an LLM-shaped verification plan
and never pretends that an API call occurred.

For online generation, set a key and optionally a model/base URL:

```powershell
$env:OPENAI_API_KEY = "..."
$env:OPENAI_MODEL = "gpt-4o-mini"       # optional
$env:OPENAI_BASE_URL = "https://api.openai.com/v1"  # optional
python run_agent.py --spec examples/sample_protocol_spec.md `
  --query "reset and handshake behavior" --outdir output
```

Online output is `verification_plan.json` plus a readable
`verification_plan.md`. Candidate SVAs are drafts only:
Spec2Plan does not compile or prove them. Engineers must check clocking,
reset polarity, sampling semantics, interface naming, and design intent.

## Architecture

`ingest.py` extracts and identifies evidence chunks. `retrieve.py` combines
lexical overlap and a local TF-IDF vector representation. `generate.py` creates
offline evidence reports or calls the configured provider and validates the
result. `run_agent.py` is the CLI boundary.

## Tests

```powershell
pytest
```

The tests cover ingestion metadata and stable IDs, retrieval ranking, Pydantic
validation, invalid citation rejection, and offline CLI behavior. They do not
need an API key. No schema pass-rate, protocol-coverage, or SVA-correctness
claim is made by this MVP.

## Limitations

PDF extraction depends on text being extractable; malformed or unsupported PDFs
are reported as errors rather than silently producing evidence. The vector
component is local TF-IDF rather than a neural embedding service. Retrieval is
not a substitute for engineering review, and generated plans are only as
grounded as the supplied document and retrieved passages.

## Attribution

See [UPSTREAM_ATTRIBUTION.md](UPSTREAM_ATTRIBUTION.md) for research inspiration.
Spec2Plan does not copy AssertLLM source code.
