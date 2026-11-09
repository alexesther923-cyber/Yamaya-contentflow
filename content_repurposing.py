# YAMAYA CONTENTFLOW
# Content Repurposing Studio
from brand_profiles import get_brand_profile
"""
Transforms existing source material into
brand-aligned content for different platforms.
"""


def validate_source_input(source_text, brand_name, output_format):
    """
    Checks whether the user's source material
    and selected options are valid.
    """

    if not isinstance(source_text, str):
        raise TypeError("Source material must be text.")

    if not source_text.strip():
        raise ValueError("Please provide source material.")

    if not isinstance(brand_name, str) or not brand_name.strip():
        raise ValueError("Please select a valid brand.")

    get_brand_profile(brand_name)

    allowed_formats = [
        "Carousel",
        "Reel",
        "Blog Article",
        "Newsletter",
        "Social Media Caption"
    ]

    if output_format not in allowed_formats:
        raise ValueError("Unsupported content format.")

    return True

