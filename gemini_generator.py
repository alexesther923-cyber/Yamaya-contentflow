
# YAMAYA CONTENTFLOW
# AI-Powered Content Strategy and Generation Tool

import os
from google import genai


def generate_content_ideas(topic, audience, format_type, tone):

    # Retrieve API key securely
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    # Connect to Gemini
    client = genai.Client(api_key=api_key)

    model = "gemini-3.5-flash-lite"

    # STAGE 1: Generate five content ideas
    ideas_prompt = f"""
You are the senior content strategist for Yamaya Afrique,
a Nigerian digital publication covering youth culture,
lifestyle and entertainment.

BRAND VOICE:
- Authentic African Gen Z storytelling.
- Witty, relatable and culturally aware.
- Conversational and intelligent.
- Funny when appropriate, without forcing slang.
- Natural, never robotic.

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
- Avoid repetitive or predictable ideas.
- Do not invent statistics or specific cultural facts.
- Avoid stereotypes and forced slang.
- Make the ideas relevant to the audience.
- Keep the ideas practical for a Nigerian digital publication.

Return only the five numbered ideas.
"""

    try:
        ideas_response = client.models.generate_content(
            model=model,
            contents=ideas_prompt
        )

        ideas = ideas_response.text

        if not ideas:
            return "The AI did not return any content ideas. Please try again."

        # STAGE 2: Develop the strongest idea
        development_prompt = f"""
You are the senior creative editor for Yamaya Afrique.

Yamaya Afrique is a Nigerian digital publication covering
youth culture, lifestyle and entertainment.

BRAND VOICE:
- Authentic African Gen Z storytelling.
- Witty, relatable and culturally aware.
- Conversational, intelligent and entertaining.
- Natural rather than robotic.
- Funny when appropriate, without forcing slang.

CONTENT BRIEF:
Topic: {topic}
Target audience: {audience}
Content format: {format_type}
Preferred tone: {tone}

THE FIVE IDEAS GENERATED:
{ideas}

YOUR TASK:

Select the strongest idea from the five ideas above.
Explain briefly why it is the strongest.

Then develop that idea into a complete, publication-ready
content draft.

IF THE FORMAT IS CAROUSEL:
1. Write an attention-grabbing cover slide.
2. Create 6-8 engaging content slides.
3. Give each slide a clear heading and complete copy.
4. End with a strong closing slide and CTA.
5. Make the slides flow naturally from beginning to end.

IF THE FORMAT IS REEL:
1. Write a strong opening hook.
2. Create a complete 30-60 second video script.
3. Include suggested scenes and visual directions.
4. Include on-screen text.
5. End with a relevant CTA.

ALSO PROVIDE:

CAPTION:
Write a natural caption that complements the content
and encourages conversation.

CALL TO ACTION:
Provide one clear, relevant CTA.

HASHTAGS:
Suggest 5-8 relevant hashtags.

EDITORIAL RULES:
- Stay relevant to the topic and audience.
- Do not invent statistics, events or specific experiences.
- Avoid stereotypes and forced Nigerian slang.
- Avoid generic AI-sounding expressions.
- Do not repeat the same point unnecessarily.
- Keep the content practical for a real editorial team.

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

        # Combine both stages
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
