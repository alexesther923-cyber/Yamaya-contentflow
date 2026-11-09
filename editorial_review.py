# YAMAYA CONTENTFLOW
# Editorial Quality and Claim Review

import os
import json
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
  PART 4: FINAL EDITORIAL STATUS

Choose exactly ONE status:

1. APPROVED FOR EDITORIAL QUALITY
No significant writing, clarity or brand alignment
problems were identified. This does not mean facts
have been verified.

2. REVISION REQUIRED
Writing, clarity, tone, structure or brand alignment
problems need correction.

3. HUMAN VERIFICATION REQUIRED
Important factual, scientific, technical, health-related
or product-related claims lack sufficient evidence.

4. DO NOT PUBLISH
Serious misleading claims, dangerous misinformation,
fabricated evidence or unsupported guarantees remain.

STATUS SELECTION RULES:

- Choose the most serious applicable status.
- If content needs revision and fact-checking,
  prioritise HUMAN VERIFICATION REQUIRED.
- If serious misleading or potentially harmful claims
  remain, choose DO NOT PUBLISH.
- Never approve content merely because it is well written.
- Never describe AI review as proof of factual accuracy.
- Briefly explain why the selected status was chosen.
FINAL OUTPUT FORMAT:

Return your entire review as valid JSON.

Use exactly this structure:

{{
  "claims": [
    {{
      "claim": "Exact claim from the submitted content",
      "claim_type": "Factual, Scientific, Health-related, Product-related, Opinion, or Creative",
      "evidence_status": "Supporting source provided, No supporting source provided, Cannot assess, or Internally inconsistent",
      "review_confidence": "High, Medium, or Low",
      "human_verification_required": true,
      "reason": "Why the claim needs attention",
      "evidence_needed": "What evidence would help verify it"
    }}
  ],
  "editorial_quality": [
    "List each writing or brand alignment issue"
  ],
  "recommended_corrections": [
    "List practical suggested improvements"
  ],
  "final_status": "APPROVED FOR EDITORIAL QUALITY, REVISION REQUIRED, HUMAN VERIFICATION REQUIRED, or DO NOT PUBLISH",
  "status_reason": "Brief explanation of the selected status"
}}

IMPORTANT:
- Return valid JSON only.
- Do not use Markdown code fences.
- Use true or false for boolean values, not text.
- Do not omit any of the required fields.
- Do not invent claims that are absent from the submitted content.
- If there are no relevant claims or issues, return an empty array.
"""
    try:
        response = client.models.generate_content(
            model=model,
            contents=review_prompt
        )

        if not response.text:
            return "The editorial review returned no result."

        try:
            parsed_response = json.loads(response.text)
        except json.JSONDecodeError:
            return "The editorial review returned an invalid JSON response."

        if not isinstance(parsed_response, dict):
            return "Invalid review format: expected a JSON object."

        required_fields = {
            "claims",
            "editorial_quality",
            "recommended_corrections",
            "final_status",
            "status_reason"
        }

        missing_fields = required_fields - parsed_response.keys()

                if missing_fields:
            return (
                "Incomplete editorial review. Missing fields: "
                + ", ".join(sorted(missing_fields))
            )

        list_fields = [
            "claims",
            "editorial_quality",
            "recommended_corrections"
        ]

        for field in list_fields:
            if not isinstance(parsed_response[field], list):
                return (
                    f"Invalid editorial review: "
                    f"'{field}' must be a list."
                )

        if not isinstance(parsed_response["final_status"], str):
            return "Invalid editorial review: final_status must be text."

        if not isinstance(parsed_response["status_reason"], str):
            return "Invalid editorial review: status_reason must be text."

        return parsed_response
    except Exception as error:
        return (
            f"Editorial review failed: "
            f"{type(error).__name__}: {error}"
        )
