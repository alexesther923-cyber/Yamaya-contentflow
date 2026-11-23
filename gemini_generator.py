
import os
from google import genai
from auth import get_brand_profile_data


def generate_content_ideas(
    topic,
    audience,
    format_type,
    tone,
    brand_name
):
    # Retrieve the selected brand's saved profile from Supabase.
    brand_profile = get_brand_profile_data(brand_name)

    if not brand_profile:
        raise ValueError(
            f"Brand profile for '{brand_name}' could not be found."
        )

    # Extract the selected brand's identity.
    description = brand_profile.get("description") or ""
    purpose = brand_profile.get("purpose") or ""
    target_audience = brand_profile.get("target_audience") or ""
    brand_values = brand_profile.get("brand_values") or ""
    tone_of_voice = brand_profile.get("tone_of_voice") or ""
    personality = brand_profile.get("brand_personality") or ""
    content_pillars = brand_profile.get("content_pillars") or ""
    content_restrictions = brand_profile.get("content_restrictions") or ""
    key_messages = brand_profile.get("key_messages") or ""

    # Retrieve API key securely.
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    client = genai.Client(api_key=api_key)
    model = "gemini-3.5-flash-lite"

    brand_context = f"""
BRAND NAME:
{brand_profile["name"]}

BRAND DESCRIPTION:
{description}

BRAND PURPOSE:
{purpose}

TARGET AUDIENCE:
{target_audience}

BRAND VALUES:
{brand_values}

TONE OF VOICE:
{tone_of_voice}

BRAND PERSONALITY:
{personality}

CONTENT PILLARS:
{content_pillars}

CONTENT RESTRICTIONS:
{content_restrictions}

KEY MESSAGES:
{key_messages}
"""

    # STAGE 1: Generate five content ideas.
    ideas_prompt = f"""
You are the content strategist for {brand_profile["name"]}.

{brand_context}

CONTENT BRIEF:
Topic: {topic}
Target audience: {audience}
Format: {format_type}
Preferred tone: {tone}

TASK:
Generate exactly FIVE original content ideas.

For each idea, include:
1. A catchy headline.
2. A short description.
3. An engaging opening hook.

EDITORIAL RULES:
- Follow the selected brand's identity.
- Respect its content pillars and restrictions.
- Make the ideas relevant to the target audience.
- Avoid repetitive or predictable ideas.
- Do not invent statistics or specific cultural facts.
- Do not use another brand's identity.
- Keep the ideas practical for the selected brand.

Return only the five numbered ideas.
"""

    try:
        ideas_response = client.models.generate_content(
            model=model,
            contents=ideas_prompt
        )

        ideas = ideas_response.text

        if not ideas:
            return (
                "The AI did not return any content ideas. "
                "Please try again."
            )

        # STAGE 2: Develop the strongest idea.
        development_prompt = f"""
You are the senior creative editor for {brand_profile["name"]}.

{brand_context}

CONTENT BRIEF:
Topic: {topic}
Target audience: {audience}
Content format: {format_type}
Preferred tone: {tone}

THE FIVE IDEAS GENERATED:
{ideas}

YOUR TASK:

Select the strongest idea from the five ideas above.
Briefly explain why it is the strongest.

Develop that idea into a complete content draft suitable
for the selected brand.

IF THE FORMAT IS CAROUSEL:
1. Write an attention-grabbing cover slide.
2. Create 6-8 engaging content slides.
3. Give each slide a clear heading and complete copy.
4. End with a strong closing slide and CTA.
5. Make the slides flow naturally.

IF THE FORMAT IS REEL:
1. Write a strong opening hook.
2. Create a complete 30-60 second video script.
3. Include suggested scenes and visual directions.
4. Include on-screen text.
5. End with a relevant CTA.

ALSO PROVIDE:

CAPTION:
Write a natural caption that complements the content.

CALL TO ACTION:
Provide one clear, relevant CTA.

HASHTAGS:
Suggest 5-8 relevant hashtags.

EDITORIAL RULES:
- Follow the selected brand's identity.
- Respect its content pillars and restrictions.
- Avoid unsupported statistics and claims.
- Do not fabricate quotes or research findings.
- Avoid generic AI-sounding expressions.
- Avoid unnecessary repetition.
- Do not introduce another brand's voice.
- Keep the content practical for the selected brand.

Use clear headings and organise the output properly.
"""

        development_response = client.models.generate_content(
            model=model,
            contents=development_prompt
        )

        developed_content = development_response.text

        if not developed_content:
            return (
                "Five ideas were generated, but the full content "
                "could not be developed. Please try again."
            )

        return (
            "========== FIVE CONTENT IDEAS ==========\n\n"
            + ideas
            + "\n\n========== DEVELOPED CONTENT ==========\n\n"
            + developed_content
        )

    except Exception as error:
        return (
            f"Gemini request failed: "
            f"{type(error).__name__}: {error}"
        )
