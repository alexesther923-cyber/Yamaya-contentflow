
# YAMAYA CONTENTFLOW
# Editorial Quality Review

import os
from google import genai
from brand_profiles import get_brand_profile


def review_content(
    content,
    brand_name="Yamaya Afrique"
):
    """
    Reviews generated content for editorial quality.
    Flags issues that need human attention.
    """

    # Retrieve the selected brand profile
    brand_profile = get_brand_profile(brand_name)

    brand_description = brand_profile["description"]

    brand_voice = "\n".join(
        brand_profile["brand_voice"]
    )

    writing_guidelines = "\n".join(
        brand_profile["writing_guidelines"]
    )

    # Retrieve API key securely
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    # Connect to Gemini
    client = genai.Client(api_key=api_key)

    model = "gemini-3.5-flash-lite"

    review_prompt = f"""
You are an experienced editorial quality reviewer.

Review the following content for {brand_profile["brand_name"]}.

BRAND DESCRIPTION:
{brand_description}

BRAND VOICE:
{brand_voice}

WRITING GUIDELINES:
{writing_guidelines}

CONTENT TO REVIEW:
{content}

REVIEW THE CONTENT FOR:

1. FACTUAL ACCURACY
Identify claims, statistics, quotes or statements
that may be unsupported or require verification.

2. TECHNICAL ACCURACY
Identify scientific, educational or technical
statements that may be misleading or oversimplified.

3. BRAND ALIGNMENT
Check whether the content follows the brand's
voice, audience and writing guidelines.

4. WRITING QUALITY
Identify awkward wording, repetition, clichés,
poor flow, spelling and grammar issues.

5. CONTENT CREDIBILITY
Identify invented experiences, assumptions,
unsubstantiated product claims or exaggerated promises.

IMPORTANT RULES:

- Do not invent sources or research findings.
- Do not claim that a statement is verified unless
  reliable supporting evidence is provided.
- Distinguish confirmed problems from claims that
  simply need further checking.
- Do not automatically rewrite questionable facts.
- Explain why each flagged issue matters.
- If you find no obvious issue in a category,
  say so without claiming the content is factually verified.

PRESENT YOUR REVIEW UNDER THESE HEADINGS:

EDITORIAL REVIEW SUMMARY

ISSUES THAT NEED ATTENTION

FACTS AND CLAIMS TO VERIFY

BRAND ALIGNMENT

WRITING AND PRESENTATION

RECOMMENDED CORRECTIONS

FINAL EDITORIAL VERDICT

Use clear, practical language.
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=review_prompt
        )

        if not response.text:
            return "The editorial review returned no result."

        return response.text

    except Exception as error:
        return (
            f"Editorial review failed: "
            f"{type(error).__name__}: {error}"
        )
