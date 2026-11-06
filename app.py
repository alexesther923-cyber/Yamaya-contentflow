
# YAMAYA CONTENTFLOW
# Main AI-powered application

from gemini_generator import generate_content_ideas
from editorial_review import review_content


def main():
    print("WELCOME TO YAMAYA CONTENTFLOW")
    print("--------------------------------")

    print("\nSELECT A WORKFLOW")
    print("1. Generate new content")
    print("2. Review existing content")

    workflow = input("\nEnter your choice (1 or 2): ")

    print("\nSELECT A BRAND")
    print("1. Yamaya Afrique")
    print("2. ErikaL Naturals")

    brand_choice = input("\nEnter your choice (1 or 2): ")

    if brand_choice == "1":
        brand_name = "Yamaya Afrique"
    elif brand_choice == "2":
        brand_name = "ErikaL Naturals"
    else:
        print("Invalid brand selection.")
        return

    if workflow == "1":

        topic = input("\nEnter your content topic: ")
        audience = input("Who is your target audience? ")
        format_type = input("Content format (Reel or Carousel): ")
        tone = input("Preferred tone: ")

        print("\nGenerating your content ideas...")

        try:
            result = generate_content_ideas(
                topic,
                audience,
                format_type,
                tone,
                brand_name
            )

            print("\n========== GENERATED CONTENT ==========")
            print(result)

        except Exception as error:
            print("\nSomething went wrong:")
            print(error)

    elif workflow == "2":

        content = input(
            "\nPaste the content you want to review:\n"
        )

        print("\nReviewing your content...")

        try:
            result = review_content(
                content,
                brand_name
            )

            print("\n========== EDITORIAL REVIEW ==========")
            print(result)

        except Exception as error:
            print("\nSomething went wrong:")
            print(error)

    else:
        print("Invalid workflow selection.")


if __name__ == "__main__":
    main()
