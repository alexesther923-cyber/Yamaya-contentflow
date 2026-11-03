# YAMAYA CONTENTFLOW
# Gemini AI Content Generator

import os
from google import genai


def generate_content_ideas(topic, audience, format_type, tone):

    # Retrieve API key securely from environment
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Gemini API key not found.")

    # Connect to Gemini
    client = genai.Client(api_key=api_key)

    # Create the content generation prompt
    prompt = f"""
    You are the content strategist for Yamaya Afrique,
    a Nigerian digital publication covering youth culture,
    lifestyle and entertainment.

    Generate 5 original content ideas.

    Topic: {topic}
    Target audience: {audience}
    Content format: {format_type}
    Preferred tone: {tone}

    For each idea, provide:
    1. A catchy headline.
    2. A short description.
    3. A suggested hook.

    Use an authentic Nigerian Gen Z voice.
    Avoid generic ideas and forced slang.
    """

    # Generate content using Gemini
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text
