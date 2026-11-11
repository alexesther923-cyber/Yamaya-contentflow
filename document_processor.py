
# YAMAYA CONTENTFLOW
# Multi-Source Document and Image Processing

import os
import pymupdf
import pytesseract

from PIL import Image
from pypdf import PdfReader
from docx import Document


def extract_text_from_image(file_path):
    """
    Extracts text from JPG, JPEG and PNG images
    using Tesseract OCR.
    """

    image = Image.open(file_path)

    extracted_text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    return extracted_text


def extract_text_from_pdf(file_path):
    """
    Extracts text from normal and scanned PDFs.

    First attempts ordinary text extraction.
    If little or no text is found, OCR is used.
    """

    reader = PdfReader(file_path)

    extracted_pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""
        extracted_pages.append(page_text)

    extracted_text = "\n".join(extracted_pages)

    # Use OCR if the PDF has no extractable text.
    if len(extracted_text.strip()) >= 20:
        return extracted_text

    # Open the PDF for OCR processing.
    pdf_document = pymupdf.open(file_path)

    ocr_pages = []

    for page in pdf_document:
        pix = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        page_text = pytesseract.image_to_string(
            image,
            lang="eng"
        )

        ocr_pages.append(page_text)

    pdf_document.close()

    return "\n".join(ocr_pages)


def extract_text_from_document(file_path):
    """
    Extracts text from PDF, DOCX and image files.
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            "The selected file could not be found."
        )

    file_extension = os.path.splitext(
        file_path
    )[1].lower()

    if file_extension == ".pdf":

        text = extract_text_from_pdf(file_path)

    elif file_extension == ".docx":

        document = Document(file_path)

        paragraphs = [
            paragraph.text
            for paragraph in document.paragraphs
        ]

        text = "\n".join(paragraphs)

    elif file_extension in [".jpg", ".jpeg", ".png"]:

        text = extract_text_from_image(file_path)

    else:
        raise ValueError(
            "Unsupported file type. "
            "Please provide a PDF, DOCX, JPG, JPEG or PNG file."
        )

    if not text.strip():
        raise ValueError(
            "No readable text was found in this file. "
            "Please check the document or image quality."
        )

    return text
