
# YAMAYA CONTENTFLOW
# Document Input and Text Extraction

import os
from pypdf import PdfReader
from docx import Document


def extract_text_from_document(file_path):
    """
    Extracts text from PDF and Word documents.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            "The selected document could not be found."
        )

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":

        reader = PdfReader(file_path)

        extracted_text = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            extracted_text.append(page_text)

        text = "\n".join(extracted_text)

    elif file_extension == ".docx":

        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
        ]

        text = "\n".join(paragraphs)

    else:
        raise ValueError(
            "Unsupported document type. "
            "Please upload a PDF or DOCX file."
        )

    if not text.strip():
        raise ValueError(
            "No readable text was found in this document. "
            "It may be an image-only or scanned PDF."
        )

    return text

