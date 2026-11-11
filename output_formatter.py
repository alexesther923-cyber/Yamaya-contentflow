
import os
from datetime import datetime
from docx import Document
from docx.shared import Pt


def save_generated_content(generated_content, brand_name):
    if not isinstance(generated_content, dict) or not generated_content:
        raise ValueError("No generated content to save.")

    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []

    document = Document()

    document.add_heading("YAMAYA CONTENTFLOW", 0)
    document.add_paragraph(f"Brand: {brand_name}")
    document.add_paragraph(
        f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}"
    )

    document.add_paragraph(
        "AI-assisted content draft. Human editorial review is required."
    )

    for format_name, content in generated_content.items():
        document.add_heading(format_name, level=1)

        for line in str(content).splitlines():
            line = line.strip()

            if not line:
                continue

            if line.startswith("**") and line.endswith("**"):
                document.add_heading(
                    line.strip("*").strip(), level=2
                )
            elif line.startswith("**") and ":" in line:
                clean_line = line.replace("**", "")
                paragraph = document.add_paragraph()
                label, value = clean_line.split(":", 1)
                paragraph.add_run(label + ":").bold = True
                paragraph.add_run(value)
            else:
                document.add_paragraph(line.replace("**", ""))

    for style_name in ["Normal", "Heading 1", "Heading 2"]:
        document.styles[style_name].font.name = "Arial"

    document.styles["Normal"].font.size = Pt(11)

    filename = (
        f"{brand_name.replace(' ', '_')}_ContentFlow_{timestamp}.docx"
    )

    file_path = os.path.join(output_folder, filename)
    document.save(file_path)

    saved_files.append(file_path)

    return saved_files
