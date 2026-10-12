import hashlib
import re
from pathlib import Path
from typing import Iterable, List

from .models import EvidenceChunk


def _chunk_id(filename: str, page: int | None, heading: str | None, text: str) -> str:
    value = f"{filename}|{page or ''}|{heading or ''}|{text}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:16]


def _split_text(text: str, filename: str, page: int | None = None) -> Iterable[EvidenceChunk]:
    heading: str | None = None
    buffer: List[str] = []
    for line in text.replace("\r\n", "\n").splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if match:
            if buffer:
                content = "\n".join(buffer).strip()
                if content:
                    yield EvidenceChunk(
                        id=_chunk_id(filename, page, heading, content),
                        text=content,
                        source_filename=filename,
                        page_number=page,
                        section_heading=heading,
                    )
                buffer = []
            heading = match.group(1).strip()
        elif line.strip():
            buffer.append(line.strip())
        elif buffer:
            content = "\n".join(buffer).strip()
            yield EvidenceChunk(
                id=_chunk_id(filename, page, heading, content),
                text=content,
                source_filename=filename,
                page_number=page,
                section_heading=heading,
            )
            buffer = []
    if buffer:
        content = "\n".join(buffer).strip()
        yield EvidenceChunk(
            id=_chunk_id(filename, page, heading, content),
            text=content,
            source_filename=filename,
            page_number=page,
            section_heading=heading,
        )


def ingest_document(path: str | Path) -> List[EvidenceChunk]:
    """Extract chunks from Markdown, text, or PDF while preserving source metadata."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    suffix = source.suffix.lower()
    if suffix in {".md", ".markdown", ".txt"}:
        return list(_split_text(source.read_text(encoding="utf-8"), source.name))
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(source))
            chunks: List[EvidenceChunk] = []
            for number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                chunks.extend(_split_text(text, source.name, number))
            return chunks
        except Exception as exc:
            raise ValueError(f"Unable to parse PDF {source.name}: {exc}") from exc
    raise ValueError(f"Unsupported document type: {source.suffix}")
