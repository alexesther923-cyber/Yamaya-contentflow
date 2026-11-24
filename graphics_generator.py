
# YAMAYA CONTENTFLOW
# Structured, Editable Brand Graphics Engine

import io
import os
import re

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")

CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1350


# --------------------------------------------------
# BRAND CONFIGURATION
# --------------------------------------------------

def extract_brand_colors(brand_colors):
    """Extract valid hexadecimal colours from a brand profile."""

    if isinstance(brand_colors, (list, tuple)):
        brand_colors = " ".join(str(c) for c in brand_colors)

    if not isinstance(brand_colors, str):
        raise ValueError("Brand colours must be text or a list.")

    colors = re.findall(r"#[0-9A-Fa-f]{6}\b", brand_colors)

    if len(colors) < 3:
        raise ValueError("At least three brand colours are required.")

    return [color.upper() for color in colors]


def load_fonts():
    """Load the brand's headline and body fonts."""

    paths = {
        "headline": os.path.join(
            FONTS_DIR,
            "Fredoka-VariableFont_wdth,wght.ttf"
        ),
        "body": os.path.join(
            FONTS_DIR,
            "Inter-VariableFont_opsz,wght.ttf"
        ),
        "bold": os.path.join(
            FONTS_DIR,
            "Inter_18pt-Bold.ttf"
        )
    }

    for path in paths.values():
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"Required font file not found: {path}"
            )

    return paths


# --------------------------------------------------
# EDITABLE SLIDE MODEL
# --------------------------------------------------

def create_slide(slide_id, layout, background, elements):
    """
    Create a structured slide.

    Elements remain independent and editable.
    """

    if not isinstance(elements, list):
        raise TypeError("Slide elements must be a list.")

    return {
        "slide_id": slide_id,
        "layout": layout,
        "canvas": {
            "width": CANVAS_WIDTH,
            "height": CANVAS_HEIGHT
        },
        "background": background,
        "elements": elements
    }


def create_text(
    element_id,
    content,
    x,
    y,
    width,
    height,
    font="body",
    font_size=40,
    color="#28231F",
    align="left",
    valign="top",
    line_spacing=12,
    min_font_size=18
):
    """Create an independently editable text element."""

    return {
        "id": element_id,
        "type": "text",
        "content": str(content),
        "position": {"x": x, "y": y},
        "size": {"width": width, "height": height},
        "font": font,
        "font_size": font_size,
        "min_font_size": min_font_size,
        "color": color,
        "align": align,
        "valign": valign,
        "line_spacing": line_spacing
    }


def create_shape(
    element_id,
    shape,
    x,
    y,
    width,
    height,
    fill,
    radius=0,
    outline=None,
    outline_width=0
):
    """Create an independently editable graphic shape."""

    allowed_shapes = [
        "rectangle",
        "rounded_rectangle",
        "ellipse",
        "line"
    ]

    if shape not in allowed_shapes:
        raise ValueError(f"Unsupported shape: {shape}")

    return {
        "id": element_id,
        "type": "shape",
        "shape": shape,
        "position": {"x": x, "y": y},
        "size": {"width": width, "height": height},
        "fill": fill,
        "radius": radius,
        "outline": outline,
        "outline_width": outline_width
    }


# --------------------------------------------------
# TEXT LAYOUT
# --------------------------------------------------

def wrap_text(text, font, draw, max_width):
    """Wrap text to fit a specified width."""

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

    for size in range(starting_size, minimum_size - 1, -2):

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


# --------------------------------------------------
# ELEMENT RENDERING
# --------------------------------------------------

def render_shape(draw, element):
    """Render an individual shape element."""

    x = element["position"]["x"]
    y = element["position"]["y"]

    width = element["size"]["width"]
    height = element["size"]["height"]

    shape = element["shape"]

    bounds = (
        x,
        y,
        x + width,
        y + height
    )

    fill = element.get("fill")
    outline = element.get("outline")
    outline_width = element.get("outline_width", 0)

    if shape == "rectangle":

        draw.rectangle(
            bounds,
            fill=fill,
            outline=outline,
            width=outline_width
        )

    elif shape == "rounded_rectangle":

        draw.rounded_rectangle(
            bounds,
            radius=element.get("radius", 20),
            fill=fill,
            outline=outline,
            width=outline_width
        )

    elif shape == "ellipse":

        draw.ellipse(
            bounds,
            fill=fill,
            outline=outline,
            width=outline_width
        )

    elif shape == "line":

        draw.line(
            (x, y, x + width, y + height),
            fill=fill,
            width=max(1, outline_width)
        )


def render_text(draw, element, fonts):
    """Render an individual text element."""

    font_type = element.get("font", "body")

    if font_type not in fonts:
        raise ValueError(f"Unknown font type: {font_type}")

    font_path = fonts[font_type]

    x = element["position"]["x"]
    y = element["position"]["y"]

    width = element["size"]["width"]
    height = element["size"]["height"]

    font, lines, line_height = fit_text(
        element["content"],
        font_path,
        draw,
        width,
        height,
        element["font_size"],
        element.get("min_font_size", 18),
        element.get("line_spacing", 12)
    )

    total_height = len(lines) * line_height

    if total_height > height:
        raise ValueError(
            f"Text element '{element['id']}' exceeds its available height."
        )

    valign = element.get("valign", "top")

    if valign == "middle":
        y += (height - total_height) // 2

    elif valign == "bottom":
        y += height - total_height

    align = element.get("align", "left")

    for line in lines:

        line_width = draw.textbbox(
            (0, 0),
            line,
            font=font
        )[2]

        if align == "center":
            text_x = x + (width - line_width) // 2

        elif align == "right":
            text_x = x + width - line_width

        else:
            text_x = x

        draw.text(
            (text_x, y),
            line,
            font=font,
            fill=element.get("color", "#28231F")
        )

        y += line_height


# --------------------------------------------------
# SLIDE RENDERER
# --------------------------------------------------

def render_slide(slide, fonts=None):
    """
    Render structured slide data into a Pillow image.

    The original slide data remains unchanged.
    """

    if not isinstance(slide, dict):
        raise TypeError("Slide must be a dictionary.")

    if fonts is None:
        fonts = load_fonts()

    canvas = slide["canvas"]

    width = canvas["width"]
    height = canvas["height"]

    image = Image.new(
        "RGB",
        (width, height),
        slide["background"]
    )

    draw = ImageDraw.Draw(image)

    for element in slide["elements"]:

        element_type = element["type"]

        if element_type == "shape":

            render_shape(draw, element)

        elif element_type == "text":

            render_text(draw, element, fonts)

        else:

            raise ValueError(
                f"Unsupported element type: {element_type}"
            )

    return image


# --------------------------------------------------
# CAROUSEL RENDERING
# --------------------------------------------------

def render_carousel(slides):
    """Render a list of editable slides into PNG-ready images."""

    if not isinstance(slides, list) or not slides:
        raise ValueError("Provide at least one slide.")

    fonts = load_fonts()

    images = []

    for slide in slides:

        images.append(
            render_slide(
                slide,
                fonts=fonts
            )
        )

    return images


# --------------------------------------------------
# PNG EXPORT
# --------------------------------------------------

def graphic_to_png(image):
    """Convert a rendered graphic into downloadable PNG bytes."""

    output = io.BytesIO()

    image.save(
        output,
        format="PNG",
        optimize=True
    )

    output.seek(0)

    return output


def carousel_to_png(images):
    """Convert rendered carousel slides into PNG byte streams."""

    return [
        graphic_to_png(image)
        for image in images
    ]


# --------------------------------------------------
# FIRST CAROUSEL TEST
# --------------------------------------------------

def build_relationships_carousel(brand_colors):
    """
    Build the first Yamaya Afrique carousel.

    Content:
    Nigerian University Relationships

    The returned slides contain editable structured data,
    not flattened images.
    """

    colors = extract_brand_colors(brand_colors)

    cream = colors[0]
    orange = colors[1]
    brown = colors[2]

    dark = colors[5] if len(colors) > 5 else "#28231F"

    slides = []

    # SLIDE 1: EDITORIAL COVER

    slides.append(
        create_slide(
            "slide_01",
            "editorial_cover",
            cream,
            [
                create_text(
                    "brand",
                    "YAMAYA AFRIQUE",
                    75, 75, 600, 55,
                    "bold", 30, dark
                ),

                create_shape(
                    "cover_accent",
                    "rectangle",
                    75, 180, 140, 14,
                    orange
                ),

                create_text(
                    "cover_title",
                    "NIGERIAN UNIVERSITY RELATIONSHIPS",
                    75, 300, 930, 440,
                    "headline", 112, brown,
                    line_spacing=12
                ),

                create_text(
                    "cover_subtitle",
                    "A course nobody registered for.",
                    80, 850, 850, 130,
                    "body", 48, dark,
                    line_spacing=15
                ),

                create_text(
                    "cover_footer",
                    "100-LEVEL FEELINGS. FINAL-YEAR COMPLICATIONS.",
                    75, 1190, 930, 60,
                    "bold", 24, brown
                )
            ]
        )
    )

    # SLIDE 2: BOLD STATEMENT

    slides.append(
        create_slide(
            "slide_02",
            "bold_statement",
            dark,
            [
                create_text(
                    "slide_number",
                    "02 / 07",
                    75, 75, 200, 45,
                    "bold", 26, orange
                ),

                create_text(
                    "statement",
                    "YOU PEOPLE ARE NOT DATING.",
                    75, 300, 930, 390,
                    "headline", 112, cream,
                    line_spacing=15
                ),

                create_shape(
                    "statement_accent",
                    "rectangle",
                    75, 790, 240, 16,
                    orange
                ),

                create_text(
                    "explanation",
                    "But somehow, you have a timetable for when to call, a routine for good morning texts and an unspoken agreement not to ask questions.",
                    75, 870, 900, 300,
                    "body", 42, cream,
                    line_spacing=18
                )
            ]
        )
    )

    # SLIDE 3: CONVERSATION

    slides.append(
        create_slide(
            "slide_03",
            "conversation",
            cream,
            [
                create_text(
                    "slide_number",
                    "03 / 07",
                    75, 75, 200, 45,
                    "bold", 26, brown
                ),

                create_shape(
                    "message_one",
                    "rounded_rectangle",
                    75, 260, 850, 230,
                    orange,
                    radius=35
                ),

                create_text(
                    "message_one_text",
                    "I WAS IN CLASS.",
                    115, 325, 770, 120,
                    "headline", 76, dark,
                    valign="middle"
                ),

                create_shape(
                    "message_two",
                    "rounded_rectangle",
                    220, 560, 790, 190,
                    brown,
                    radius=35
                ),

                create_text(
                    "message_two_text",
                    "THREE HOURS LATER...",
                    260, 600, 710, 110,
                    "headline", 58, cream,
                    valign="middle"
                ),

                create_text(
                    "explanation",
                    "Last seen. Status. Followers. Every available clue.",
                    75, 870, 900, 180,
                    "body", 42, dark,
                    line_spacing=18
                )
            ]
        )
    )

    # SLIDE 4: EDITORIAL COMMENTARY

    slides.append(
        create_slide(
            "slide_04",
            "editorial_commentary",
            orange,
            [
                create_text(
                    "slide_number",
                    "04 / 07",
                    75, 75, 200, 45,
                    "bold", 26, dark
                ),

                create_text(
                    "statement",
                    "YOUR RELATIONSHIP IS NOW A FACULTY MATTER.",
                    75, 250, 930, 470,
                    "headline", 105, dark,
                    line_spacing=12
                ),

                create_shape(
                    "divider",
                    "rectangle",
                    75, 810, 930, 8,
                    brown
                ),

                create_text(
                    "explanation",
                    "Your coursemates know. Your roommates know. Even the person selling snacks near your lecture hall has an opinion.",
                    75, 880, 900, 250,
                    "body", 39, dark,
                    line_spacing=18
                )
            ]
        )
    )

    # SLIDE 5: MINIMALIST STATEMENT

    slides.append(
        create_slide(
            "slide_05",
            "minimal_statement",
            cream,
            [
                create_text(
                    "slide_number",
                    "05 / 07",
                    75, 75, 200, 45,
                    "bold", 26, brown
                ),

                create_text(
                    "headline",
                    "LOVE IS SWEET.",
                    75, 330, 930, 170,
                    "headline", 112, brown
                ),

                create_text(
                    "headline_two",
                    "TRANSPORT FARE IS NOT.",
                    75, 500, 930, 240,
                    "headline", 105, orange
                ),

                create_text(
                    "explanation",
                    "Sometimes the biggest relationship test is figuring out how to see each other without spending your entire weekly allowance.",
                    75, 850, 900, 260,
                    "body", 40, dark,
                    line_spacing=18
                )
            ]
        )
    )

    # SLIDE 6: EDITORIAL STATEMENT

    slides.append(
        create_slide(
            "slide_06",
            "editorial_statement",
            brown,
            [
                create_text(
                    "slide_number",
                    "06 / 07",
                    75, 75, 200, 45,
                    "bold", 26, orange
                ),

                create_text(
                    "headline",
                    "YOU SAID YOU WOULD READ TOGETHER.",
                    75, 270, 930, 390,
                    "headline", 100, cream,
                    line_spacing=14
                ),

                create_shape(
                    "accent",
                    "rectangle",
                    75, 750, 170, 14,
                    orange
                ),

                create_text(
                    "explanation",
                    "Somehow, two hours later, neither of you has opened the course material.",
                    75, 850, 900, 230,
                    "body", 43, cream,
                    line_spacing=18
                )
            ]
        )
    )

    # SLIDE 7: CLOSING

    slides.append(
        create_slide(
            "slide_07",
            "editorial_closing",
            dark,
            [
                create_text(
                    "brand",
                    "YAMAYA AFRIQUE",
                    75, 75, 600, 55,
                    "bold", 30, orange
                ),

                create_text(
                    "closing_question",
                    "BE HONEST. WHICH ONE HAVE YOU EXPERIENCED?",
                    75, 310, 930, 400,
                    "headline", 100, cream,
                    line_spacing=15
                ),

                create_shape(
                    "closing_accent",
                    "rectangle",
                    75, 800, 220, 15,
                    orange
                ),

                create_text(
                    "call_to_action",
                    "Tell us the most unserious thing you've witnessed in a Nigerian campus relationship.",
                    75, 880, 900, 220,
                    "body", 40, cream,
                    line_spacing=18
                ),

                create_text(
                    "footer",
                    "WE KNOW YOU'VE GOT STORIES.",
                    75, 1190, 900, 55,
                    "bold", 27, orange
                )
            ]
        )
    )

    return slides
# --------------------------------------------------
# AUTOMATIC DESIGN SELECTION
# --------------------------------------------------

def select_layout(content, role=None):
    """
    Recommend a visual layout based on the purpose
    and characteristics of the slide content.

    An explicitly supplied role takes priority.
    """

    content = str(content).strip()
    text = content.lower()

    if not content:
        raise ValueError("Slide content cannot be empty.")

    # Explicit content roles
    role_layouts = {
        "cover": "editorial_cover",
        "introduction": "editorial_cover",
        "statement": "bold_statement",
        "conversation": "conversation",
        "explanation": "editorial_commentary",
        "minimal": "minimal_statement",
        "closing": "editorial_closing",
        "question": "editorial_closing",
        "comparison": "comparison_layout",
        "list": "list_layout",
        "statistic": "fact_layout",
        "photo": "photo_led"
    }

    if role:
        normalized_role = str(role).strip().lower()

        if normalized_role not in role_layouts:
            raise ValueError(
                f"Unsupported content role: {role}"
            )

        return role_layouts[normalized_role]

    # Automatic content analysis
    if "?" in content and len(content.split()) <= 14:
        return "editorial_closing"

    if (
        "\n" in content
        or '"' in content
        or "said:" in text
        or "replied:" in text
    ):
        return "conversation"

    if any(
        marker in text
        for marker in ["top 5", "top 10", "steps:", "first,", "second,"]
    ):
        return "list_layout"

    if any(
        marker in text
        for marker in ["compared with", "versus", " vs ", "difference between"]
    ):
        return "comparison_layout"

    if any(
        marker in text
        for marker in ["%", "percent", "statistics show", "survey found"]
    ):
        return "fact_layout"

    word_count = len(content.split())

    if word_count <= 7:
        return "minimal_statement"

    if word_count >= 30:
        return "editorial_commentary"

    return "bold_statement"
