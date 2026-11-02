"""Local document storage and lightweight retrieval for assistant answers."""
import hashlib
import os
from pathlib import Path
import re
import shutil
import sys


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOP_WORDS = {
    "about", "after", "also", "and", "are", "can", "does", "for", "from",
    "how", "into", "its", "our", "the", "their", "this", "that", "then",
    "there", "these", "they", "what", "when", "where", "which", "who",
    "will", "with", "would", "you", "your",
}
_CHUNK_WORDS = 150
_CHUNK_OVERLAP = 25
_MAX_MATCHES = 3
_MAX_CONTEXT_CHARS = 2200


class DocumentError(ValueError):
    """Raised when a document cannot be imported or read."""


def get_document_directory():
    """Return a per-user document directory that survives app upgrades."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "LightningVoiceAssistant" / "documents"


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8-sig").strip()
    except UnicodeDecodeError as error:
        raise DocumentError(f"{path.name} is not valid UTF-8 text.") from error


def extract_document_text(path):
    """Extract text from a supported local document."""
    path = Path(path)
    extension = path.suffix.casefold()
    if extension in {".txt", ".md"}:
        text = _read_text(path)
    elif extension == ".docx":
        from zipfile import BadZipFile
        from xml.etree import ElementTree
        from zipfile import ZipFile

        try:
            with ZipFile(path) as archive:
                document_xml = archive.read("word/document.xml")
            root = ElementTree.fromstring(document_xml)
        except (BadZipFile, KeyError, ElementTree.ParseError, OSError) as error:
            raise DocumentError(f"{path.name} is not a readable DOCX document.") from error
        paragraphs = []
        for paragraph in root.iter():
            if paragraph.tag.endswith("}p"):
                paragraph_text = "".join(
                    node.text or "" for node in paragraph.iter()
                    if node.tag.endswith("}t")
                )
                if paragraph_text:
                    paragraphs.append(paragraph_text)
        text = "\n".join(paragraphs).strip()
    elif extension == ".pdf":
        try:
            from pypdf import PdfReader
            from pypdf.errors import PdfReadError
        except ImportError as error:
            raise DocumentError(
                "PDF support is unavailable. Reinstall the app to include its PDF reader."
            ) from error
        try:
            reader = PdfReader(str(path))
            if reader.is_encrypted:
                raise DocumentError(f"{path.name} is password-protected.")
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        except DocumentError:
            raise
        except (OSError, ValueError, PdfReadError) as error:
            raise DocumentError(f"{path.name} is not a readable PDF document.") from error
    else:
        raise DocumentError(
            f"Unsupported file type: {path.suffix or '(no extension)'}. "
            "Choose a TXT, Markdown, PDF, or DOCX file."
        )

    if not text:
        detail = " Scanned PDFs need OCR before import." if extension == ".pdf" else ""
        raise DocumentError(
            f"No readable text was found in {path.name}.{detail}"
        )
    return text


def _file_digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_document(source_path, document_directory=None):
    """Validate and copy one document into the user's persistent library."""
    source = Path(source_path)
    extract_document_text(source)

    directory = Path(document_directory or get_document_directory())
    directory.mkdir(parents=True, exist_ok=True)
    digest = _file_digest(source)
    target = directory / source.name
    if target.exists():
        if _file_digest(target) == digest:
            return target
        target = directory / f"{source.stem}-{digest[:8]}{source.suffix}"
        if target.exists() and _file_digest(target) == digest:
            return target
        suffix = 2
        while target.exists():
            target = directory / f"{source.stem}-{digest[:8]}-{suffix}{source.suffix}"
            suffix += 1

    shutil.copy2(source, target)
    return target


def list_documents(document_directory=None):
    """List imported documents in a stable, user-friendly order."""
    directory = Path(document_directory or get_document_directory())
    if not directory.exists():
        return []
    return sorted(
        (path for path in directory.iterdir()
         if path.is_file() and path.suffix.casefold() in SUPPORTED_EXTENSIONS),
        key=lambda path: path.name.casefold(),
    )


def remove_document(filename, document_directory=None):
    """Remove a single imported document without allowing paths outside the library."""
    directory = Path(document_directory or get_document_directory())
    name = Path(filename).name
    if name != filename or not name:
        raise DocumentError("Select a document from the library to remove.")
    target = directory / name
    if target.suffix.casefold() not in SUPPORTED_EXTENSIONS or not target.is_file():
        raise DocumentError(f"{name} is not in the document library.")
    target.unlink()


def _chunks(text):
    words = text.split()
    if not words:
        return []
    step = _CHUNK_WORDS - _CHUNK_OVERLAP
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + _CHUNK_WORDS, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step
    return chunks


def search_documents(query, document_directory=None):
    """Return a small set of relevant local excerpts for a user question."""
    query_terms = {
        word.casefold() for word in _WORD_RE.findall(query or "")
        if len(word) > 2 and word.casefold() not in _STOP_WORDS
    }
    if not query_terms:
        return ""

    matches = []
    for path in list_documents(document_directory):
        text = extract_document_text(path)
        for index, chunk in enumerate(_chunks(text)):
            chunk_terms = {word.casefold() for word in _WORD_RE.findall(chunk)}
            title_terms = {word.casefold() for word in _WORD_RE.findall(path.stem)}
            overlap = query_terms & (chunk_terms | title_terms)
            if overlap:
                score = len(overlap) / len(query_terms)
                score += 0.1 * len(query_terms & title_terms)
                matches.append((score, path.name.casefold(), index, path.name, chunk))

    matches.sort(key=lambda item: (-item[0], item[1], item[2]))
    excerpts = []
    total_chars = 0
    for _score, _name, _index, filename, chunk in matches:
        excerpt = chunk[:900]
        formatted = f"[{filename}]\n{excerpt}"
        if total_chars + len(formatted) > _MAX_CONTEXT_CHARS:
            continue
        excerpts.append(formatted)
        total_chars += len(formatted)
        if len(excerpts) >= _MAX_MATCHES:
            break
    return "\n\n".join(excerpts)
