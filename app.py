

from gemini_generator import generate_content_ideas
from editorial_review import review_content
from contentflow_pipeline import run_contentflow_pipeline
from output_formatter import save_generated_content
from google.colab import files


def offer_save(content, brand_name):
    choice = input("\nSave this output? (y/n): ").strip().lower()

    if choice == "y":
        saved_files = save_generated_content(content, brand_name)
        print("\nFiles saved successfully!")

        for path in saved_files:
            print("Downloading:", path)
            files.download(path)


def main():
    print("\nWELCOME TO YAMAYA CONTENTFLOW")
    print("--------------------------------")
    print("1. Generate new content")
    print("2. Review existing content")
    print("3. Repurpose existing content")

    workflow = input("\nSelect workflow (1, 2 or 3): ")

    print("\nSELECT A BRAND")
    print("1. Yamaya Afrique")
    print("2. ErikaL Naturals")

    brands = {"1": "Yamaya Afrique", "2": "ErikaL Naturals"}
    brand_choice = input("Select brand (1 or 2): ")

    if brand_choice not in brands:
        print("Invalid brand selection.")
        return

    brand_name = brands[brand_choice]

    if workflow == "1":
        topic = input("Enter content topic: ")
        audience = input("Enter target audience: ")
        format_type = input("Format (Reel or Carousel): ")
        tone = input("Preferred tone: ")

        try:
            result = generate_content_ideas(
                topic, audience, format_type, tone, brand_name
            )
            print("\nGENERATED CONTENT\n", result)
            offer_save({"Content Ideas": result}, brand_name)
        except Exception as error:
            print("Error:", error)

    elif workflow == "2":
        content = input("Paste content for review:\n")

        try:
            result = review_content(content, brand_name)
            print("\nEDITORIAL REVIEW\n", result)
        except Exception as error:
            print("Error:", error)

    elif workflow == "3":
        print("\nSOURCE OPTIONS")
        print("1. Paste text")
        print("2. Upload PDF or DOCX")

        source_choice = input("Choose source (1 or 2): ")
        source_text = None
        file_path = None

        if source_choice == "1":
            source_text = input("\nPaste your source material:\n")
        elif source_choice == "2":
            uploaded = files.upload()

            if not uploaded:
                print("No file uploaded.")
                return

            file_path = next(iter(uploaded))

            if not file_path.lower().endswith((".pdf", ".docx")):
                print("Unsupported file. Upload a PDF or DOCX.")
                return
        else:
            print("Invalid source selection.")
            return

        print("\nOUTPUT FORMATS")
        format_options = {
            "1": "Carousel",
            "2": "Reel",
            "3": "Blog Article",
            "4": "Newsletter",
            "5": "Social Media Caption"
        }

        for number, name in format_options.items():
            print(f"{number}. {name}")

        choices = input("Choose formats separated by commas: ")

        try:
            selected_formats = [
                format_options[x.strip()]
                for x in choices.split(",")
            ]

            if not selected_formats:
                raise ValueError("Select at least one format.")

            if len(set(selected_formats)) != len(selected_formats):
                raise ValueError("Duplicate formats are not allowed.")

            result = run_contentflow_pipeline(
                brand_name=brand_name,
                output_formats=selected_formats,
                source_text=source_text,
                file_path=file_path
            )

            generated = result["generated_content"]

            print("\nREPURPOSED CONTENT")

            for format_name, content in generated.items():
                print(f"\n--- {format_name.upper()} ---")
                print(content)

            offer_save(generated, brand_name)

        except (KeyError, ValueError) as error:
            print("Invalid selection:", error)
        except Exception as error:
            print("Error:", error)

    else:
        print("Invalid workflow selection.")


if __name__ == "__main__":
    main()
