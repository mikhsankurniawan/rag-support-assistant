from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader


async def extract_text_from_upload(file: UploadFile) -> str:
    content = await file.read()
    filename = file.filename or "uploaded_file"
    content_type = file.content_type or "application/octet-stream"

    if filename.lower().endswith(".pdf") or content_type == "application/pdf":
        return _extract_pdf_text(content)

    if filename.lower().endswith((".txt", ".md", ".csv")) or content_type.startswith("text/"):
        return content.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Please upload PDF, TXT, MD, or CSV for this MVP.")


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)
