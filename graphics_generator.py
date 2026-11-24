
# YAMAYA CONTENTFLOW
# Local Brand Graphics Generator

import io
import os
import re

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350


def extract_brand_colors(brand_colors):
    """Extract valid hexadecimal colours from a brand profile."""

    if isinstance(brand_colors, (list, tuple)):
        brand_colors = " ".join(str(color) for color in brand_colors)

    if not isinstance(brand_colors, str):
        raise ValueError("Brand colours must be provided as text or a list.")

    colors = re.findall(r"#[0-9A-Fa-f]{6}\b", brand_colors)

    if len(colors) < 3:
        raise ValueError(
            "At least three valid brand colours are required."
        )

    return [color.upper() for color in colors]


def load_fonts():
    """Load the brand fonts from the repository's fonts directory."""

    headline_path = os.path.join(
        FONTS_DIR,
        "Fredoka-VariableFont_wdth,wght.ttf"
    )

    body_path = os.path.join(
        FONTS_DIR,
        "Inter-VariableFont_opsz,wght.ttf"
    )

    bold_path = os.path.join(
        FONTS_DIR,
        "Inter_18pt-Bold.ttf"
    )

    for font_path in [headline_path, body_path, bold_path]:
        if not os.path.isfile(font_path):
            raise FileNotFoundError(
                f"Required font file not found: {font_path}"
            )

    return {
        "headline_path": headline_path,
        "body_path": body_path,
        "bold": ImageFont.truetype(bold_path, 30)
    }


def wrap_text(text, font, draw, max_width):
    """Wrap text to fit within a specified width."""

    words = str(text).split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()

        text_width = draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )[2]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)

            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def fit_text(
    text,
    font_path,
    draw,
    max_width,
    max_height,
    starting_size,
    minimum_size,
    line_spacing
):
    """Find a font size that fits the available text area."""

    for size in range(
        starting_size,
        minimum_size - 1,
        -2
    ):
        font = ImageFont.truetype(font_path, size)

        lines = wrap_text(
            text,
            font,
            draw,
            max_width
        )

        line_height = size + line_spacing
        total_height = len(lines) * line_height

        if total_height <= max_height:
            return font, lines, line_height

    font = ImageFont.truetype(font_path, minimum_size)

    lines = wrap_text(
        text,
        font,
        draw,
        max_width
    )

    line_height = minimum_size + line_spacing

    return font, lines, line_height


def generate_graphic(
    title,
    body,
    brand_colors,
    brand_name="Yamaya Afrique"
):
    """Generate a 1080 x 1350 branded editorial graphic."""

    if not str(title).strip():
        raise ValueError("Please provide a graphic title.")

    if not str(body).strip():
        raise ValueError("Please provide graphic body text.")

    colors = extract_brand_colors(brand_colors)

    background_color = colors[0]
    accent_color = colors[1]
    dark_color = colors[2]

    fonts = load_fonts()

    image = Image.new(
        "RGB",
        (CANVAS_WIDTH, CANVAS_HEIGHT),
        background_color
    )

    draw = ImageDraw.Draw(image)

    # Editorial frame
    draw.rounded_rectangle(
        (55, 55, 1025, 1295),
        radius=35,
        outline=dark_color,
        width=3
    )

    # Decorative circle
    draw.ellipse(
        (850, 80, 1080, 310),
        fill=accent_color
    )

    draw.ellipse(
        (930, 160, 1020, 250),
        fill=background_color
    )

    # Brand name
    draw.text(
        (95, 105),
        brand_name.upper(),
        font=fonts["bold"],
        fill=dark_color
    )

    # Accent line
    draw.rounded_rectangle(
        (95, 190, 250, 205),
        radius=7,
        fill=accent_color
    )

    # Fit title into its available space
    title_font, title_lines, title_line_height = fit_text(
        title,
        fonts["headline_path"],
        draw,
        max_width=850,
        max_height=350,
        starting_size=84,
        minimum_size=52,
        line_spacing=18
    )

    # Keep titles to a maximum of three lines
    if len(title_lines) > 3:
        title_lines = title_lines[:3]
        title_lines[-1] = title_lines[-1].rstrip(".,;:") + "..."

    title_y = 290

    for line in title_lines:
        draw.text(
            (95, title_y),
            line,
            font=title_font,
            fill=dark_color
        )

        title_y += title_line_height

    # Calculate remaining space for body text
    body_y = title_y + 55
    body_bottom = 1100
    body_height = body_bottom - body_y

    if body_height <= 0:
        raise ValueError(
            "The title is too long for this graphic layout."
        )

    # Fit body text into remaining space
    body_font, body_lines, body_line_height = fit_text(
        body,
        fonts["body_path"],
        draw,
        max_width=850,
        max_height=body_height,
        starting_size=36,
        minimum_size=24,
        line_spacing=18
    )

    # Prevent body text from entering the footer
    max_body_lines = max(
        1,
        body_height // body_line_height
    )

    if len(body_lines) > max_body_lines:
        body_lines = body_lines[:max_body_lines]
        body_lines[-1] = body_lines[-1].rstrip(".,;:") + "..."

    for line in body_lines:
        draw.text(
            (95, body_y),
            line,
            font=body_font,
            fill=dark_color
        )

        body_y += body_line_height

    # Bottom editorial accent
    draw.rounded_rectangle(
        (95, 1160, 985, 1168),
        radius=4,
        fill=accent_color
    )

    draw.text(
        (95, 1195),
        brand_name,
        font=fonts["bold"],
        fill=dark_color
    )

    return image


def graphic_to_png(image):
    """Convert a generated graphic into downloadable PNG bytes."""

    output = io.BytesIO()

    image.save(
        output,
        format="PNG",
        optimize=True
    )

    output.seek(0)

    return output
