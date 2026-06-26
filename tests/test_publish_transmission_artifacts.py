import tempfile
import unittest
from pathlib import Path

from scripts.publish_transmission import metadata_for, render_canon_index, write_pdf


class TransmissionArtifactTests(unittest.TestCase):
    def test_metadata_includes_portable_artifact_paths(self):
        data = {
            "ID": "CC-TX-2026-06-26-001",
            "Title": "Ada Vance Team Welcome",
            "Date": "2026-06-26",
            "Status": "Active Canon",
            "Type": "Team Onboarding",
            "Layer": "Personnel / Project Onboarding",
            "From": "Cody Valle",
            "To": "Brandon Hatfield, LPC",
            "Authorized By": "Brandon Hatfield, LPC",
            "Summary": "Ada joins the council.",
        }

        metadata = metadata_for(data, ["team-onboarding"], Path("2026/CC-TX-2026-06-26-001"))

        self.assertEqual(metadata["html_path"], "2026/CC-TX-2026-06-26-001/index.html")
        self.assertEqual(metadata["pdf_path"], "2026/CC-TX-2026-06-26-001/transmission.pdf")
        self.assertEqual(metadata["markdown_path"], "transmissions/2026/CC-TX-2026-06-26-001.md")

    def test_canon_index_links_to_html_pdf_and_markdown(self):
        manifest = {
            "entries": [
                {
                    "id": "CC-TX-2026-06-26-001",
                    "title": "Ada Vance Team Welcome",
                    "status": "Active Canon",
                    "layer": "Personnel / Project Onboarding",
                    "summary": "Ada joins the council.",
                    "html_path": "2026/CC-TX-2026-06-26-001/index.html",
                    "pdf_path": "2026/CC-TX-2026-06-26-001/transmission.pdf",
                    "markdown_path": "transmissions/2026/CC-TX-2026-06-26-001.md",
                    "date": "2026-06-26",
                }
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            previous = Path.cwd()
            try:
                import os

                os.chdir(tmpdir)
                render_canon_index(manifest)
                canon = Path("CANON.md").read_text(encoding="utf-8")
            finally:
                os.chdir(previous)

        self.assertIn("## Current Active Canon", canon)
        self.assertIn("CC-TX-2026-06-26-001 - Ada Vance Team Welcome", canon)
        self.assertIn("archive/2026/CC-TX-2026-06-26-001/index.html", canon)
        self.assertIn("archive/2026/CC-TX-2026-06-26-001/transmission.pdf", canon)
        self.assertIn("transmissions/2026/CC-TX-2026-06-26-001.md", canon)

    def test_pdf_writer_creates_pdf_file(self):
        data = {
            "ID": "CC-TX-2026-06-26-001",
            "Title": "Ada Vance Team Welcome",
            "Date": "2026-06-26",
            "Status": "Active Canon",
            "Layer": "Personnel / Project Onboarding",
            "From": "Cody Valle",
            "To": "Brandon Hatfield, LPC",
            "Authorized By": "Brandon Hatfield, LPC",
            "Summary": "Ada joins the council.",
            "Body": "Ada validates assumptions and anchors future architecture in standards.",
            "Decisions": "- Ada joins the council.",
            "Next Actions": "- Maintain portable canon.",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "transmission.pdf"
            write_pdf(data, path)
            payload = path.read_bytes()

        self.assertTrue(payload.startswith(b"%PDF-1.4"))
        self.assertIn(b"%%EOF", payload)


if __name__ == "__main__":
    unittest.main()
