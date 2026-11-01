"""Render existing QA PDFs with bundled PDFium (no LibreOffice needed)."""
from pathlib import Path
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[2]


def main():
    for path in sorted((ROOT / "part5/.qa").glob("*/*.pdf")):
        with pdfium.PdfDocument(str(path)) as doc:
            for i in range(len(doc)):
                page = doc[i]
                bitmap = page.render(scale=1.6)
                bitmap.to_pil().save(path.parent / f"page-{i+1}.png")
                bitmap.close()
                page.close()
            print(path.stem, len(doc), "pages rendered")


if __name__ == "__main__":
    main()
