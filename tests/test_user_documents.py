import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from user_documents import (
    DocumentError,
    add_document,
    extract_document_text,
    get_document_directory,
    list_documents,
    remove_document,
    search_documents,
)


def _write_text_pdf(path, text):
    content = f"BT /F1 18 Tf 20 100 Td ({text}) Tj ET".encode("ascii")
    objects = (
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode("ascii") + b" >>\nstream\n"
        + content + b"\nendstream",
    )
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(body + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(pdf)


class UserDocumentsTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.library = self.root / "library"
        self.source = self.root / "source"
        self.source.mkdir()

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_import_persists_text_documents_and_deduplicates(self):
        source = self.source / "guide.txt"
        source.write_text("Deployment uses a local Ollama model.", encoding="utf-8")

        imported = add_document(source, self.library)
        duplicate = add_document(source, self.library)

        self.assertEqual(imported, duplicate)
        self.assertEqual([imported], list_documents(self.library))
        self.assertEqual(
            "Deployment uses a local Ollama model.",
            extract_document_text(imported),
        )

    def test_same_name_with_different_content_is_kept(self):
        original = self.source / "guide.md"
        original.write_text("First deployment guide.", encoding="utf-8")
        add_document(original, self.library)
        original.write_text("Second deployment guide.", encoding="utf-8")

        imported = add_document(original, self.library)

        self.assertNotEqual(imported.name, original.name)
        self.assertEqual(2, len(list_documents(self.library)))

    def test_import_extracts_docx_and_pdf_text(self):
        docx = self.source / "manual.docx"
        with zipfile.ZipFile(docx, "w") as archive:
            archive.writestr(
                "word/document.xml",
                '<w:document xmlns:w="urn:test"><w:body>'
                '<w:p><w:r><w:t>Installation manual</w:t></w:r></w:p>'
                '<w:p><w:r><w:t>Supports Windows and Mac</w:t></w:r></w:p>'
                '</w:body></w:document>',
            )
        pdf = self.source / "manual.pdf"
        _write_text_pdf(pdf, "Installation manual for Windows and Mac")

        self.assertEqual(
            "Installation manual\nSupports Windows and Mac",
            extract_document_text(docx),
        )
        self.assertIn("Windows and Mac", extract_document_text(pdf))

    def test_scanned_pdf_without_text_gets_an_actionable_error(self):
        pdf = self.source / "scanned.pdf"
        _write_text_pdf(pdf, "")

        with self.assertRaisesRegex(DocumentError, "need OCR"):
            extract_document_text(pdf)

    def test_search_returns_relevant_excerpt_and_ignores_unrelated_query(self):
        source = self.source / "deployment.md"
        source.write_text(
            "Deployment guide. Ollama runs locally and stores the selected model "
            "on the user's computer. Windows and Mac users can import documentation.",
            encoding="utf-8",
        )
        add_document(source, self.library)

        result = search_documents("Where does Ollama store its model?", self.library)

        self.assertIn("[deployment.md]", result)
        self.assertIn("stores the selected model", result)
        self.assertEqual("", search_documents("zebra telescope", self.library))

    def test_rejects_unsupported_and_textless_documents(self):
        unsupported = self.source / "notes.csv"
        unsupported.write_text("some,data", encoding="utf-8")
        blank = self.source / "empty.txt"
        blank.write_text("  ", encoding="utf-8")

        with self.assertRaisesRegex(DocumentError, "Unsupported file type"):
            add_document(unsupported, self.library)
        with self.assertRaisesRegex(DocumentError, "No readable text"):
            add_document(blank, self.library)
        self.assertEqual([], list_documents(self.library))

    def test_remove_document_rejects_paths_outside_library(self):
        source = self.source / "reference.txt"
        source.write_text("A local reference.", encoding="utf-8")
        imported = add_document(source, self.library)

        with self.assertRaises(DocumentError):
            remove_document("../reference.txt", self.library)
        remove_document(imported.name, self.library)
        self.assertEqual([], list_documents(self.library))

    def test_macos_storage_uses_user_application_support(self):
        with (
            patch("user_documents.os.name", "posix"),
            patch("user_documents.sys.platform", "darwin"),
            patch("user_documents.Path.home", return_value=self.root),
        ):
            directory = get_document_directory()

        self.assertEqual(
            self.root / "Library" / "Application Support"
            / "LightningVoiceAssistant" / "documents",
            directory,
        )


if __name__ == "__main__":
    unittest.main()
