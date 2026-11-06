# YAMAYA CONTENTFLOW
# Editorial Quality and Claim Review

import os
from google import genai
from brand_profiles import get_brand_profile


def review_content(
    content,
    brand_name="Yamaya Afrique"
):
    """
    Reviews content for factual reliability,
    technical accuracy, brand alignment and writing quality.
    """

    brand_profile = get_brand_profile(brand_name)

    brand_description = brand_profile["description"]

    brand_voice = "\n".join(
        brand_profile["brand_voice"]
    )

    writing_guidelines = "\n".join(
        brand_profile["writing_guidelines"]
    )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    client = genai.Client(api_key=api_key)

    model = "gemini-3.5-flash-lite"

    review_prompt = f"""
You are a careful editorial reviewer working with
{brand_profile["brand_name"]}.

Your task is to review the submitted content.
Be critical, fair, evidence-conscious and transparent
about uncertainty.

BRAND DESCRIPTION:
{brand_description}

BRAND VOICE:
{brand_voice}

WRITING GUIDELINES:
{writing_guidelines}

CONTENT TO REVIEW:
{content}


PART 1: CLAIM-BY-CLAIM AUDIT

Identify the important factual, scientific, technical,
health-related and product-related claims in the content.

For each claim, provide:

1. Exact claim or short quotation.
2. Claim type:
   - Factual
   - Scientific or technical
   - Health-related
   - Product-related
   - Opinion
   - Creative or subjective

3. Evidence status:
   - Supporting source provided
   - No supporting source provided
   - Cannot assess from the submitted content
   - Appears internally inconsistent

4. Review confidence:
   - High
   - Medium
   - Low

IMPORTANT:
Review confidence means how confident you are that
the claim deserves the editorial flag. It does NOT mean
the claim is scientifically or factually proven.

5. Why the claim needs attention.
6. What evidence or source type would help verify it.


PART 2: EDITORIAL QUALITY

Review the content for:

- Brand voice and audience alignment.
- Clarity and readability.
- Grammar and spelling.
- Repetition and awkward wording.
- Unsupported assumptions.
- Exaggerated promises and misleading language.
- Generic or unnatural AI-style expressions.


PART 3: RECOMMENDED CORRECTIONS

Suggest practical improvements.

Do not silently change the meaning of the original content.

For factual or scientific claims that cannot be verified,
recommend cautious wording or human verification instead
of inventing a replacement fact.


STRICT REVIEW RULES:

- Do not invent statistics, research findings, sources,
  citations, quotations or URLs.

- Do not claim that you searched or checked external
  research when you did not.

- Never present an unsupported scientific, technical,
  health-related or product-related statement as an
  established fact.

- If you cannot determine whether a claim is accurate
  from the submitted content and supplied evidence,
  explicitly say: "Requires human verification."

- Do not use general knowledge to turn an uncertain
  claim into a supposedly verified correction.

- Do not introduce new scientific explanations,
  ingredients, mechanisms or product benefits unless
  they are supported by evidence supplied with the content.

- Do not label a claim false merely because no source
  was provided.

- Distinguish clearly between:
  1. Demonstrably incorrect claims.
  2. Unsupported claims.
  3. Claims requiring specialist verification.
  4. Opinions and creative statements.

- When suggesting a correction to an unsupported claim,
  prefer removing the claim, qualifying it, or requesting
  evidence rather than replacing it with another factual
  assertion.

- Never invent product benefits or imply that a product
  has been tested when no testing evidence is provided.

- A lack of obvious issues does not mean the content
  has been fact-checked.
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
