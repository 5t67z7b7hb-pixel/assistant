"""Small, local term search for technical interview speech and answer context."""
from difflib import SequenceMatcher
import re


_GLOSSARY = (
    {
        "term": "LLM",
        "topic": "llm_fundamentals",
        "aliases": ("large language model", "large language models", "L L M", "el el em"),
    },
    {
        "term": "RAG",
        "topic": "rag",
        "aliases": ("retrieval augmented generation", "retrieval augmentation generation", "R A G", "R A B", "RAB"),
    },
    {
        "term": "MCP",
        "topic": "mcp",
        "aliases": ("Model Context Protocol", "M C P", "N C P", "NCP"),
    },
    {"term": "tokens", "topic": "llm_fundamentals", "aliases": ("token", "tokenization")},
    {"term": "context window", "topic": "llm_fundamentals", "aliases": ("context length", "context limit")},
    {"term": "sampling", "topic": "llm_fundamentals", "aliases": ("temperature", "top p", "top k")},
    {"term": "prompting", "topic": "llm_fundamentals", "aliases": ("prompt design", "prompt engineering")},
    {"term": "model limitations", "topic": "llm_fundamentals", "aliases": ("model limitation", "limitations of an LLM", "hallucination")},
    {"term": "document ingestion", "topic": "rag", "aliases": ("ingestion pipeline", "document ingest", "document in jesting", "document ingesting")},
    {"term": "chunking", "topic": "rag", "aliases": ("chunk", "document chunking", "text splitting")},
    {"term": "embeddings", "topic": "rag", "aliases": ("embedding", "vector embedding")},
    {"term": "vector search", "topic": "rag", "aliases": ("similarity search", "semantic search", "nearest neighbor search")},
    {"term": "reranking", "topic": "rag", "aliases": ("re ranking", "re ranker", "rank king", "rerank")},
    {"term": "citation", "topic": "rag", "aliases": ("citations", "source citation")},
    {"term": "freshness", "topic": "rag", "aliases": ("content freshness", "stale documents")},
    {"term": "MCP tools", "topic": "mcp", "aliases": ("tools call", "tool execution")},
    {"term": "MCP resources", "topic": "mcp", "aliases": ("resource", "resources")},
    {"term": "MCP prompts", "topic": "mcp", "aliases": ("prompt template", "prompt templates")},
    {"term": "metadata", "topic": "knowledge_architecture", "aliases": ("document metadata", "provenance")},
    {"term": "taxonomy", "topic": "knowledge_architecture", "aliases": ("taxonomies", "controlled vocabulary")},
    {"term": "access control", "topic": "knowledge_architecture", "aliases": ("ACL", "RBAC", "permissions")},
    {"term": "versioning", "topic": "knowledge_architecture", "aliases": ("document version", "version control")},
    {"term": "update workflow", "topic": "knowledge_architecture", "aliases": ("reindexing workflow", "content update")},
    {"term": "prompt injection", "topic": "guardrails", "aliases": ("indirect prompt injection", "injection defense", "injection defence")},
    {"term": "data privacy", "topic": "guardrails", "aliases": ("personal data", "PII")},
    {"term": "tool authorization", "topic": "guardrails", "aliases": ("tool permissions", "tool permission")},
    {"term": "output validation", "topic": "guardrails", "aliases": ("validate output", "schema validation")},
    {"term": "human review", "topic": "guardrails", "aliases": ("human approval", "human in the loop")},
    {"term": "retrieval quality", "topic": "evaluation", "aliases": ("retrieval relevance", "search quality")},
    {"term": "answer correctness", "topic": "evaluation", "aliases": ("answer accuracy", "factual correctness")},
    {"term": "citation accuracy", "topic": "evaluation", "aliases": ("citation correctness",)},
    {"term": "latency", "topic": "evaluation", "aliases": ("response time", "p95")},
    {"term": "cost", "topic": "evaluation", "aliases": ("inference cost", "token cost")},
    {"term": "safety evaluation", "topic": "evaluation", "aliases": ("safety testing", "safety eval")},
)

# These are pronunciation/transcription variants, not semantic rewrites. Keep
# the map narrow so the original words remain authoritative for the answer.
_TRANSCRIPTION_FIXES = (
    (re.compile(r"\b(?:r[\s.-]*a[\s.-]*(?:g|b))\b", re.IGNORECASE), "RAG"),
    (re.compile(r"\b(?:m[\s.-]*c[\s.-]*p|n[\s.-]*c[\s.-]*p)\b", re.IGNORECASE), "MCP"),
    (re.compile(r"\b(?:l[\s.-]*l[\s.-]*m|el[\s-]+el[\s-]+em)\b", re.IGNORECASE), "LLM"),
)

WHISPER_HOTWORDS = ", ".join((
    "LLM", "large language model", "RAG", "retrieval augmented generation",
    "MCP", "Model Context Protocol", "tokens", "context window", "sampling",
    "prompting", "document ingestion", "chunking", "embeddings", "vector search",
    "reranking", "citation", "freshness", "prompt injection", "access control",
    "tool authorization", "output validation",
    "slowly", "solely", "subtle", "subtly", "thoroughly", "particularly",
    "significantly", "approximately", "necessarily", "concurrently",
    "consequently", "albeit", "ubiquitous", "meticulous", "ambiguity",
    "feasible", "paradigm", "nuance", "hierarchy", "sustainable", "resilient",
    "comprehensive", "proprietary", "anomaly", "architecture", "throughput",
))


def canonicalize_transcription_terms(text):
    """Normalize only a few known spoken acronym variants after ASR."""
    result = text or ""
    for pattern, canonical in _TRANSCRIPTION_FIXES:
        result = pattern.sub(canonical, result)
    return result


def correct_high_confidence_terms(text):
    """Fix only narrow ASR confusions and very close technical-word spellings."""
    result = canonicalize_transcription_terms(text)
    # This phrase is a recurring speech-recognition rendering of the technical
    # phrase "document ingestion"; keep the exception explicit and narrow.
    result = re.sub(r"\bdocument\s+in\s+jesting\b", "document ingestion", result, flags=re.IGNORECASE)

    targets = {
        _tokens(item["term"])[0]
        for item in _GLOSSARY
        if len(_tokens(item["term"])) == 1 and len(_tokens(item["term"])[0]) >= 7
    }
    spans = list(re.finditer(r"[A-Za-z][A-Za-z0-9-]*", result))
    edits = []
    for match in spans:
        heard = match.group(0).casefold()
        if len(heard) < 7 or heard in targets:
            continue
        ranked = sorted(
            ((SequenceMatcher(None, heard, target, autojunk=False).ratio(), target) for target in targets),
            reverse=True,
        )
        if ranked and ranked[0][0] >= 0.91 and (len(ranked) == 1 or ranked[0][0] - ranked[1][0] >= 0.06):
            edits.append((match.start(), match.end(), ranked[0][1]))

    for start, end, canonical in reversed(edits):
        result = result[:start] + canonical + result[end:]
    return result


def _tokens(value):
    return re.findall(r"[a-z0-9]+", (value or "").casefold())


def rank_glossary_terms(text, limit=8):
    """Return local exact/fuzzy term matches for downstream context retrieval.

    Fuzzy hits are retrieval hints only: this function never rewrites the user's
    transcript. Short words are exact-match only to avoid speculative guesses.
    """
    words = _tokens(text)
    if not words:
        return []

    windows_by_size = {}
    for size in range(1, min(5, len(words)) + 1):
        windows_by_size[size] = [
            " ".join(words[index:index + size])
            for index in range(len(words) - size + 1)
        ]

    best_by_term = {}
    for item in _GLOSSARY:
        candidates = (item["term"],) + item["aliases"]
        best = None
        for alias in candidates:
            alias_words = _tokens(alias)
            alias_text = " ".join(alias_words)
            if not alias_text:
                continue
            for candidate in windows_by_size.get(len(alias_words), []):
                score = SequenceMatcher(None, candidate, alias_text, autojunk=False).ratio()
                if score == 1.0:
                    best = (score, candidate, alias)
                    break
                # Similarity search may retrieve context for a long, slightly
                # misheard phrase; it must not silently change the transcript.
                if len(alias_text.replace(" ", "")) >= 7 and score >= 0.84:
                    if best is None or score > best[0]:
                        best = (score, candidate, alias)
            if best and best[0] == 1.0:
                break
        if best:
            previous = best_by_term.get(item["term"])
            if previous is None or best[0] > previous["score"]:
                best_by_term[item["term"]] = {
                    "term": item["term"],
                    "topic": item["topic"],
                    "matched": best[1],
                    "score": round(best[0], 2),
                }

    return sorted(best_by_term.values(), key=lambda item: item["score"], reverse=True)[:limit]
