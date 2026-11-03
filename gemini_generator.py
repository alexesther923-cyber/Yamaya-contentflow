
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

    # Content generation instructions
    prompt = f"""
You are the senior content strategist and creative writer
for Yamaya Afrique.

BRAND IDENTITY:
Yamaya Afrique is a Nigerian digital publication covering
youth culture, lifestyle and entertainment.

Our voice is:
- Authentic African Gen Z storytelling.
- Witty, relatable and culturally aware.
- Conversational, intelligent and entertaining.
- Funny when appropriate, without forcing slang.
- Natural rather than robotic or overly promotional.

CONTENT BRIEF:

Topic: {topic}
Target audience: {audience}
Content format: {format_type}
Preferred tone: {tone}

YOUR TASK:

PART 1: CONTENT IDEAS

Generate 5 original content ideas based on the topic.

For each idea, provide:
1. A catchy headline.
2. A short description.
3. An engaging opening hook.

Avoid repetitive, generic or predictable ideas.

PART 2: DEVELOP THE BEST IDEA

Choose the strongest of the five ideas and develop it
into a complete piece of content.

If the selected format is CAROUSEL:

1. Cover slide with an attention-grabbing headline.
2. Six to eight informative and engaging slides.
3. A strong closing slide with a clear CTA.
4. Make every slide interesting enough to encourage
   the audience to keep swiping.

If the selected format is REEL:

1. A strong opening hook.
2. A complete 30-60 second video script.
3. Suggested visual directions and scenes.
4. On-screen text.
5. A closing CTA.

PART 3: CAPTION

Write a natural social media caption that:
- Complements the content.
- Sounds like Yamaya Afrique.
- Encourages conversation and engagement.
- Avoids generic AI-sounding expressions.

PART 4: CALL TO ACTION

Provide one clear and relevant CTA.

PART 5: HASHTAGS

Suggest 5-8 relevant hashtags.

IMPORTANT EDITORIAL RULES:

- Do not invent specific campus experiences, locations,
  statistics or cultural facts.
- Avoid stereotypes about Nigerian students or young people.
- Do not use forced Nigerian slang.
- Avoid unnecessarily offensive or inappropriate content.
- Keep the content relevant to the stated audience.
- Prioritise originality, clarity and shareability.
- Do not repeat the same idea in different words.

Use clear headings and organise the output for easy
use by a social media content team.

Remember: The final content should feel like something
a real Yamaya Afrique editorial team would publish.
"""

    # Generate content using Gemini
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        return response.text

    except Exception as error:
        return (
            f"Gemini request failed: "
            f"{type(error).__name__}: {error}"
        )
