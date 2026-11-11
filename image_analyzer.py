
# YAMAYA CONTENTFLOW
# AI Image Analysis

import os
import mimetypes

from google import genai
from google.genai import types


def analyze_image(image_path, question=None):
    """
    Uses Gemini AI to analyse an image.
    """

    if not os.path.isfile(image_path):
        raise FileNotFoundError(
            "The selected image could not be found."
        )

    mime_type, _ = mimetypes.guess_type(image_path)

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if mime_type not in allowed_types:
        raise ValueError(
            "Please provide a JPG, JPEG, PNG or WEBP image."
        )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    if question is None:
        question = (
            "Describe this image clearly. Identify visible "
            "objects, important details, text, colours and "
            "visual elements. For charts and infographics, "
            "explain the visible information. Do not guess "
            "details that cannot be confirmed from the image."
        )

    client = genai.Client(api_key=api_key)

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            question,
            image_part
        ]
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text
