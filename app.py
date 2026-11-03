# YAMAYA CONTENTFLOW
# Main AI-powered application

from gemini_generator import generate_content_ideas


def main():
    print("WELCOME TO YAMAYA CONTENTFLOW")
    print("--------------------------------")

    topic = input("Enter your content topic: ")
    audience = input("Who is your target audience? ")
    format_type = input("Content format (Reel or Carousel): ")
    tone = input("Preferred tone: ")

    print("\nGenerating your content ideas...")

    try:
        result = generate_content_ideas(
            topic,
            audience,
            format_type,
            tone
        )

        print("\n========== GENERATED CONTENT ==========")
        print(result)

    except Exception as error:
        print("\nSomething went wrong:")
        print(error)


if __name__ == "__main__":
    main()
