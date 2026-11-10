# YAMAYA CONTENTFLOW
# Content Repurposing Studio

from brand_profiles import get_brand_profile
import os
from google import genai
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


def repurpose_content(source_text, brand_name, output_format):
    """
    Transforms existing source material into
    brand-aligned content using Gemini AI.
    """

    # Check that the input is valid.
    validate_source_input(
        source_text,
        brand_name,
        output_format
    )

    # Retrieve the selected brand's profile.
    brand = get_brand_profile(brand_name)

    # Retrieve the Gemini API key.
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    # Connect to Gemini.
    client = genai.Client(api_key=api_key)

    # Instructions for the selected content format.
    format_instructions = {
        "Carousel": (
            "Create a social media carousel with 6–8 slides. "
            "Give each slide a clear heading and concise body text."
        ),

        "Reel": (
            "Create a 30–60 second Reel script. "
            "Include a hook, spoken script, and visual suggestions."
        ),

        "Blog Article": (
            "Create a well-structured blog article with a title, "
            "introduction, clear sections, and conclusion."
        ),

        "Newsletter": (
            "Create an engaging newsletter with a subject line, "
            "introduction, main sections, and closing."
        ),

        "Social Media Caption": (
            "Create an engaging social media caption with a strong "
            "opening and a relevant call to action."
        )
    }

    # Build the AI instructions.
    prompt = f"""
You are an experienced content repurposing assistant.

Your task is to transform the supplied source material
into the requested content format.

BRAND INFORMATION

Brand: {brand["brand_name"]}
Description: {brand["description"]}
Industry: {brand["industry"]}
Target audience: {brand["target_audience"]}
Brand voice: {", ".join(brand["brand_voice"])}

Writing guidelines:
{chr(10).join(brand["writing_guidelines"])}

SOURCE MATERIAL:
{source_text}

REQUESTED FORMAT:
{output_format}

FORMAT INSTRUCTIONS:
{format_instructions[output_format]}

IMPORTANT EDITORIAL RULES:

1. Treat the source material as the only factual
   authority for the content.

2. Preserve the original meaning and context.

3. Do not invent statistics, dates, locations,
   quotations, research findings, sources,
   experiences, or factual claims.

4. Do not turn general statements into specific
   events or experiences.

5. Do not add details such as specific class times,
   locations, costs, or routines unless they
   appear in the source.

6. Only use direct quotations that appear
   in the source material.

7. Do not introduce unsupported scientific,
   medical, or product performance claims.

8. Creative hooks, headlines and transitions
   are allowed, but they must not introduce
   new factual information.

9. If information is missing, leave it out
   instead of guessing.

10. Follow the selected brand's writing guidelines.

11. Use natural, human-sounding language.

12. Before returning the result, check every
    factual statement against the source material.
    Remove any statement that cannot be supported.

13. Human editorial review is still required
    before publication.

Return the completed content in the requested format.
"""

    # Generate the repurposed content.
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text
