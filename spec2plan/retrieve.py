import math
import re
from collections import Counter
from typing import List

from .models import EvidenceChunk, RetrievedEvidence

_TOKEN = re.compile(r"[a-zA-Z0-9_]+")


def _tokens(text: str) -> List[str]:
    return [token.lower() for token in _TOKEN.findall(text)]


def retrieve(chunks: List[EvidenceChunk], query: str, top_k: int = 5) -> List[RetrievedEvidence]:
    """Rank by a hybrid of normalized term overlap and TF-IDF cosine similarity."""
    if not chunks:
        return []
    query_tokens = _tokens(query)
    query_counts = Counter(query_tokens)
    documents = [_tokens(chunk.text) for chunk in chunks]
    df = Counter(token for document in documents for token in set(document))
    n_docs = len(documents)

    def vector(document: List[str]) -> dict[str, float]:
        counts = Counter(document)
        return {token: (1 + math.log(count)) * math.log((n_docs + 1) / (df[token] + 1))
                for token, count in counts.items()}

    q_vector = vector(query_tokens)
    q_norm = math.sqrt(sum(value * value for value in q_vector.values())) or 1.0
    query_set = set(query_tokens)
    scored: List[RetrievedEvidence] = []
    for chunk, document in zip(chunks, documents):
        lexical = len(query_set.intersection(document)) / (len(query_set) or 1)
        d_vector = vector(document)
        dot = sum(q_vector.get(token, 0.0) * value for token, value in d_vector.items())
        d_norm = math.sqrt(sum(value * value for value in d_vector.values())) or 1.0
        cosine = max(0.0, dot / (q_norm * d_norm))
        scored.append(RetrievedEvidence(
            chunk=chunk, score=0.55 * lexical + 0.45 * cosine,
            lexical_score=lexical, vector_score=cosine,
        ))
    scored.sort(key=lambda item: (-item.score, item.chunk.id))
    selected: List[RetrievedEvidence] = []
    seen_text: set[str] = set()
    for result in scored:
        normalized = " ".join(_tokens(result.chunk.text))
        if normalized in seen_text:
            continue
        seen_text.add(normalized)
        selected.append(result)
        if len(selected) >= top_k:
            break
    return selected
