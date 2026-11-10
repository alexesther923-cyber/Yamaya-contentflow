# YAMAYA CONTENTFLOW
# Multi-Format Content Repurposing

from content_repurposing import repurpose_content


def repurpose_into_multiple_formats(
    source_text,
    brand_name,
    output_formats
):
    """
    Repurposes one source into multiple
    selected content formats.
    """

    if not isinstance(output_formats, list):
        raise TypeError("Output formats must be a list.")

    if not output_formats:
        raise ValueError("Select at least one output format.")

    results = {}

    for output_format in output_formats:

        results[output_format] = repurpose_content(
            source_text=source_text,
            brand_name=brand_name,
            output_format=output_format
        )

    return results
