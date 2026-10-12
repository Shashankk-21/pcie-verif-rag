# Agentic RAG for Protocol Verification Planning

An agentic retrieval-augmented generation (RAG) pipeline that turns packetized protocol specifications—such as **PCI Express (PCIe)** and **AMBA AXI**—into structured verification plans. Built with **LlamaIndex** and **FastAPI**, it combines table-aware PDF parsing with hybrid retrieval (vector search + BM25) to connect protocol rules with verification checklist items and candidate **SystemVerilog Assertions (SVA)**.

## Overview

Protocol specifications contain important requirements across prose, tables, field definitions, packet layouts, timing rules, and exceptions. If extracted without their structural context, these details can be difficult to retrieve accurately and translate into testable behavior.

This project builds a RAG workflow that preserves useful PDF structure, retrieves relevant specification passages, and asks an LLM to synthesize a structured verification plan. A validation harness uses **Pydantic** and **JSON Schema** to enforce the expected verification-tracking format before results are accepted downstream.

## Key Features

- **PDF specification ingestion:** Parses protocol-document content, including tables, with attention to the structure needed for retrieval.
- **Hybrid retrieval:** Combines vector similarity search with BM25 lexical retrieval to find semantically related passages and exact protocol terminology.
- **Agentic plan generation:** Uses LlamaIndex orchestration to transform retrieved requirements into organized verification tasks.
- **Verification checklist synthesis:** Produces structured checklist items from applicable protocol rules.
- **SVA drafting:** Generates candidate SystemVerilog Assertions to help engineers express protocol properties as checks.
- **API layer:** Exposes the pipeline through FastAPI.
- **Strict output validation:** Uses Pydantic models and JSON Schema validation to enforce the verification tracking schema; the project reports **100% schema adherence** for the evaluated outputs.

## Architecture

```text
PCIe / AXI protocol PDF
          |
          v
  Table-aware PDF extraction
          |
          v
 Content normalization and metadata
 (sections, tables, page/source context where available)
          |
          v
      Indexing pipeline
          |
          +-----------------------+
          |                       |
          v                       v
   Vector retrieval          BM25 retrieval
          |                       |
          +-----------+-----------+
                      v
             Hybrid result ranking
                      |
                      v
       LlamaIndex agent / LLM synthesis
                      |
          +-----------+------------+
          |                        |
          v                        v
 Structured verification       Candidate SVA
 checklist / plan              properties
          |                        |
          +-----------+------------+
                      v
           Pydantic + JSON Schema checks
                      |
                      v
            Validated API response
```

### Typical workflow

1. **Ingest a specification:** Provide a protocol PDF supported by the document-ingestion pipeline.
2. **Extract structure:** Parse text and tables while retaining relevant document context and metadata.
3. **Build retrieval indexes:** Prepare vector representations and a BM25 index over normalized specification content.
4. **Submit a verification request:** Ask for a plan covering a protocol feature, transaction type, rule, or scenario.
5. **Retrieve supporting material:** Combine semantic and lexical retrieval to gather useful passages.
6. **Synthesize verification artifacts:** Generate a structured checklist and candidate SVA from the retrieved evidence.
7. **Validate the output:** Check generated records against Pydantic models and the required JSON Schema.
8. **Review and implement:** Have a verification engineer confirm the interpretation and adapt the candidate assertions to the design and verification environment.

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| RAG orchestration | LlamaIndex |
| API framework | FastAPI |
| Retrieval | Vector search + BM25 |
| Document processing | Table-aware PDF parsing |
| Data validation | Pydantic + JSON Schema |
| Generated verification artifacts | Structured checklists and SystemVerilog Assertions (SVA) |

## Prerequisites

- Python version supported by the project's dependencies
- An LLM provider/model configured for the pipeline
- The PDF parsing and vector-index dependencies selected by the repository
- The vector store or index backend configured by the implementation
- Git

The actual PDF parser, embedding model, vector-store backend, and LLM provider were not specified in the project summary. Document the concrete selections from the implementation here.

## Setup

The commands below are a starting point. Replace placeholders and align them with the package layout and configuration used in the repository.

```bash
git clone <repository-url>
cd <repository-directory>

python -m venv .venv
```

Activate the environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies if the repository includes a requirements file:

```bash
pip install -r requirements.txt
```

Configure the LLM provider, embedding model, and index backend through the project's documented environment variables or configuration file. Keep API keys and other secrets out of source control.

## Running the API

Start FastAPI using the module and application object defined by your repository. A common pattern is:

```bash
uvicorn <module>:<app-object> --host 127.0.0.1 --port 8000
```

The placeholders must be replaced with the actual module and FastAPI application object. If the project uses a different startup command, use that instead.

Once running, use the OpenAPI documentation exposed by the FastAPI application to inspect the implemented endpoints and request/response models. Add the exact endpoint paths and example payloads here when confirmed from the source code.

## Output and Validation

The pipeline is designed to produce structured verification artifacts, rather than unvalidated free-form prose. Pydantic models validate the generated data against application-level types and constraints, while JSON Schema validation checks conformance to the verification tracking contract.

A validated verification record may include fields defined by the project's schema, such as a requirement reference, verification objective, scenario, expected behavior, or candidate assertion. The exact field names and required structure are controlled by the implementation's schema and should be documented alongside the API contract.

The project reports **100% adherence to the verification tracking schema** for the evaluated outputs. This measures structural/schema compliance; it does **not** by itself establish that every retrieved interpretation is correct, every protocol requirement is covered, or every generated SVA compiles and proves the intended behavior.

## Evaluation and Quality Checks

Recommended checks include:

- Schema pass rate for generated verification records
- Retrieval relevance for protocol-specific queries
- Coverage of source requirements by the generated checklist
- Correctness of source context associated with each generated requirement
- SVA syntax/compile pass rate in the target verification toolchain
- Engineer review results for semantic correctness and completeness

For reproducibility, record the specification version, parsing configuration, retrieval settings, model configuration, and validation results for each evaluation run.

## Safety and Limitations

- **Review generated assertions:** Candidate SVA is a starting point and must be checked against the protocol, design intent, reset behavior, clocking, and sampling semantics.
- **Treat retrieved material as evidence:** LLM output can misread exceptions, conditions, or relationships between tables and surrounding prose.
- **Schema validity is not semantic correctness:** Valid JSON can still contain an incomplete or incorrect verification plan.
- **Version matters:** Protocol rules can vary by revision and profile. Keep document identity and version metadata available when supported.
- **Respect specification licensing:** Only ingest and distribute documents in ways permitted by their licenses and access terms.

## Suggested Repository Layout

Adapt this outline to match the real codebase.

```text
.
├── README.md
├── requirements.txt
├── app/                    # FastAPI routes and application setup
├── ingestion/              # PDF and table extraction
├── retrieval/              # Vector and BM25 retrieval
├── generation/              # Plan and SVA synthesis
├── schemas/                # Pydantic models and JSON Schema
├── tests/                  # Unit, integration, and schema tests
└── configs/                # Example, non-secret configuration
```

## Future Improvements

- Attach source-document references and page/table context to every checklist item where possible.
- Add retrieval evaluation using curated protocol questions and expected evidence passages.
- Compile candidate assertions automatically in a controlled SystemVerilog test environment.
- Add protocol-revision-aware indexing and document comparison.
- Measure requirement coverage and engineer-rated semantic correctness in addition to schema adherence.

## License
