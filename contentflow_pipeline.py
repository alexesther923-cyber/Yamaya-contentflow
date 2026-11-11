
# YAMAYA CONTENTFLOW
# End-to-End Content Generation Pipeline

from source_processor import process_source
from multi_format_repurposing import repurpose_into_multiple_formats


def run_contentflow_pipeline(
    brand_name,
    output_formats,
    source_text=None,
    file_path=None,
    image_mode="ocr",
    image_question=None
):
    """
    Processes source material and generates
    content in one or multiple formats.
    """

    # Ensure the user provides exactly one source.
    if (source_text is None) == (file_path is None):
        raise ValueError(
            "Please provide either pasted text or a file, not both."
        )

    # Extract or process the source material.
    processed_source = process_source(
        source_text=source_text,
        file_path=file_path,
        image_mode=image_mode,
        image_question=image_question
    )

    # Generate content in the selected formats.
    generated_content = repurpose_into_multiple_formats(
        source_text=processed_source,
        brand_name=brand_name,
        output_formats=output_formats
    )

    return {
        "source_text": processed_source,
        "generated_content": generated_content
    }
