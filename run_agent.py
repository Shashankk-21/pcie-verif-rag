import argparse
import json
from pathlib import Path

from spec2plan.generate import evidence_report, generate_online
from spec2plan.ingest import ingest_document
from spec2plan.retrieve import retrieve


def _markdown_report(report: dict) -> str:
    lines = [f"# Spec2Plan evidence report\n\n**Query:** {report['query']}\n",
             "## Retrieved evidence\n"]
    for entry in report["retrieved"]:
        chunk = entry["chunk"]
        location = f"{chunk['source_filename']}"
        if chunk["page_number"]:
            location += f", page {chunk['page_number']}"
        if chunk["section_heading"]:
            location += f", section {chunk['section_heading']}"
        lines.append(f"### `{chunk['id']}` ({location}, score {entry['score']:.3f})\n\n{chunk['text']}\n")
    lines.append(f"**Evidence categories:** {', '.join(report['evidence_categories']) or 'none'}\n")
    lines.append(f"**Categories without evidence:** {', '.join(report['categories_without_evidence']) or 'none'}\n")
    lines.append(f"\n_{report['note']}_\n")
    return "\n".join(lines)


def _plan_markdown(plan: dict) -> str:
    lines = [f"# Spec2Plan verification plan\n\n**Query:** {plan['query']}\n"]
    for item in plan["items"]:
        citation = ", ".join(plan_value for plan_value in [
            item.get("source_section"),
            f"page {item['source_page']}" if item.get("source_page") else None,
            f"evidence: {', '.join(item['evidence_ids'])}",
        ] if plan_value) or "not supplied"
        lines.extend([
            f"## {item['requirement_id']}: {item['requirement_statement']}\n",
            f"**Category:** {item['category']}  \n**Source:** {citation}\n",
            f"**Supporting quotation:** {item['supporting_quotation']}\n",
            f"**Objective:** {item['verification_objective']}\n",
            f"**Scenario:** {item['test_scenario']}\n",
            f"**Expected behavior:** {item['expected_behavior']}\n",
            f"**Relevant signals:** {', '.join(item['relevant_signals'])}\n",
            f"**Candidate SVA:**\n```systemverilog\n{item['candidate_sva']}\n```\n",
            f"**Clock/reset/sampling assumptions:** {item['clock_reset_sampling_assumptions']}\n",
            f"**Confidence and uncertainty:** {item['confidence_or_uncertainty']}\n",
        ])
    lines.append(f"## Categories without evidence\n\n{', '.join(plan['uncovered_categories']) or 'none reported'}\n")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build source-grounded verification plans.")
    parser.add_argument("--spec", required=True, help="Markdown, text, or PDF specification")
    parser.add_argument("--query", required=True)
    parser.add_argument("--outdir", default="output")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    chunks = ingest_document(args.spec)
    results = retrieve(chunks, args.query, args.top_k)
    output = Path(args.outdir)
    output.mkdir(parents=True, exist_ok=True)
    if args.offline:
        report = evidence_report(args.query, results)
        data = report.model_dump()
        (output / "evidence_report.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        (output / "evidence_report.md").write_text(_markdown_report(data), encoding="utf-8")
        print(f"Wrote offline evidence report with {len(results)} retrieved chunks to {output}")
    else:
        plan = generate_online(args.query, results)
        data = plan.model_dump()
        (output / "verification_plan.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        (output / "verification_plan.md").write_text(_plan_markdown(data), encoding="utf-8")
        print(f"Wrote verification plan with {len(plan.items)} items to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
