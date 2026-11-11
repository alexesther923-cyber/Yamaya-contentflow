
# YAMAYA CONTENTFLOW
# Central Source Processing Module

import os

from document_processor import extract_text_from_document
from image_analyzer import analyze_image


def process_source(
    source_text=None,
    file_path=None,
    image_mode="ocr",
    image_question=None
):
    """
    Accepts pasted text or uploaded files
    and returns text for content repurposing.
    """

    # Process pasted text
    if source_text is not None:

        if not isinstance(source_text, str):
            raise TypeError("Source material must be text.")

        if not source_text.strip():
            raise ValueError("Please provide source material.")

        return source_text.strip()

    # Process uploaded files
    if file_path is not None:

        if not os.path.isfile(file_path):
            raise FileNotFoundError(
                "The selected file could not be found."
            )

        extension = os.path.splitext(file_path)[1].lower()

        image_extensions = [
            ".jpg", ".jpeg", ".png"
        ]

        if extension in image_extensions:

            if image_mode == "ocr":
                return extract_text_from_document(file_path)

            elif image_mode == "vision":
                return analyze_image(
                    file_path,
                    image_question
                )

            else:
                raise ValueError(
                    "Image mode must be 'ocr' or 'vision'."
                )

        return extract_text_from_document(file_path)

    raise ValueError(
        "Please provide pasted text or a document."
    )
