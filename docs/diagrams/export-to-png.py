#!/usr/bin/env python3
"""
Export Excalidraw diagram to PNG

This script renders the Excalidraw JSON diagram to a PNG image
using PIL (Pillow) for high-quality output.

Requirements:
    pip install Pillow
"""

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
EXCALIDRAW_FILE = Path(__file__).parent / "flowspec-workflow.excalidraw"
OUTPUT_PNG = Path(__file__).parent / "flowspec-workflow.png"
SCALE = 2  # For high DPI
PADDING = 50


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def draw_rounded_rectangle(draw, x, y, width, height, radius, fill, outline, width_px):
    """Draw a rounded rectangle"""
    # Main rectangles
    draw.rectangle(
        [x + radius, y, x + width - radius, y + height], fill=fill, outline=None
    )
    draw.rectangle(
        [x, y + radius, x + width, y + height - radius], fill=fill, outline=None
    )

    # Corners
    draw.ellipse([x, y, x + radius * 2, y + radius * 2], fill=fill, outline=None)
    draw.ellipse(
        [x + width - radius * 2, y, x + width, y + radius * 2], fill=fill, outline=None
    )
    draw.ellipse(
        [x, y + height - radius * 2, x + radius * 2, y + height],
        fill=fill,
        outline=None,
    )
    draw.ellipse(
        [x + width - radius * 2, y + height - radius * 2, x + width, y + height],
        fill=fill,
        outline=None,
    )

    # Outline
    if outline:
        # Top and bottom
        draw.line([x + radius, y, x + width - radius, y], fill=outline, width=width_px)
        draw.line(
            [x + radius, y + height, x + width - radius, y + height],
            fill=outline,
            width=width_px,
        )

        # Left and right
        draw.line([x, y + radius, x, y + height - radius], fill=outline, width=width_px)
        draw.line(
            [x + width, y + radius, x + width, y + height - radius],
            fill=outline,
            width=width_px,
        )

        # Corner arcs
        draw.arc(
            [x, y, x + radius * 2, y + radius * 2],
            180,
            270,
            fill=outline,
            width=width_px,
        )
        draw.arc(
            [x + width - radius * 2, y, x + width, y + radius * 2],
            270,
            360,
            fill=outline,
            width=width_px,
        )
        draw.arc(
            [x, y + height - radius * 2, x + radius * 2, y + height],
            90,
            180,
            fill=outline,
            width=width_px,
        )
        draw.arc(
            [x + width - radius * 2, y + height - radius * 2, x + width, y + height],
            0,
            90,
            fill=outline,
            width=width_px,
        )


def render_excalidraw_to_png():
    """Render Excalidraw JSON to PNG"""
    print("Loading Excalidraw diagram...")
    with open(EXCALIDRAW_FILE, "r") as f:
        data = json.load(f)

    elements = data["elements"]

    # Calculate bounds
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")

    for el in elements:
        min_x = min(min_x, el["x"])
        min_y = min(min_y, el["y"])
        max_x = max(max_x, el["x"] + el.get("width", 0))
        max_y = max(max_y, el["y"] + el.get("height", 0))

    # Calculate image dimensions
    width = int((max_x - min_x + PADDING * 2) * SCALE)
    height = int((max_y - min_y + PADDING * 2) * SCALE)

    print(f"Creating image: {width}x{height} px")

    # Create image
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Transform coordinates
    def transform_x(x):
        return int((x - min_x + PADDING) * SCALE)

    def transform_y(y):
        return int((y - min_y + PADDING) * SCALE)

    # Load font with cross-platform support
    try:
        font_cache = {}

        def get_font(size):
            size_scaled = int(size * SCALE)
            if size_scaled not in font_cache:
                # Try multiple font paths for cross-platform support
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                    "/Library/Fonts/Arial.ttf",  # macOS
                    "C:\\Windows\\Fonts\\arial.ttf",  # Windows
                    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",  # Linux alternative
                ]
                for font_path in font_paths:
                    try:
                        font_cache[size_scaled] = ImageFont.truetype(
                            font_path, size_scaled
                        )
                        break
                    except Exception:
                        continue
                else:
                    # Fallback to default font if none found
                    font_cache[size_scaled] = ImageFont.load_default()
            return font_cache[size_scaled]
    except Exception:

        def get_font(size):  # noqa: ARG001
            return ImageFont.load_default()

    print("Rendering elements...")

    # Sort elements by type to ensure proper layering (shapes first, then arrows, then text)
    sorted_elements = sorted(
        elements,
        key=lambda el: (
            0
            if el["type"] in ["rectangle", "diamond"]
            else 1
            if el["type"] == "arrow"
            else 2,
            el.get("id", ""),
        ),
    )

    for el in sorted_elements:
        el_type = el["type"]
        x = transform_x(el["x"])
        y = transform_y(el["y"])

        # Parse colors
        stroke_color = el.get("strokeColor", "#1e1e1e")
        bg_color = el.get("backgroundColor", "transparent")
        opacity = el.get("opacity", 100) / 100

        stroke_rgb = hex_to_rgb(stroke_color) if stroke_color != "transparent" else None
        fill_rgb = hex_to_rgb(bg_color) if bg_color != "transparent" else None

        # Apply opacity
        if fill_rgb and opacity < 1:
            fill_rgb = tuple(int(c * opacity + 255 * (1 - opacity)) for c in fill_rgb)

        stroke_width = int(el.get("strokeWidth", 1) * SCALE)

        if el_type == "rectangle":
            w = int(el["width"] * SCALE)
            h = int(el["height"] * SCALE)
            roundness = el.get("roundness", {})

            if roundness.get("type") == 3:
                # Rounded rectangle
                radius = int(8 * SCALE)
                draw_rounded_rectangle(
                    draw, x, y, w, h, radius, fill_rgb, stroke_rgb, stroke_width
                )
            else:
                # Regular rectangle
                if fill_rgb:
                    draw.rectangle([x, y, x + w, y + h], fill=fill_rgb)
                if stroke_rgb:
                    draw.rectangle(
                        [x, y, x + w, y + h], outline=stroke_rgb, width=stroke_width
                    )

        elif el_type == "diamond":
            w = int(el["width"] * SCALE)
            h = int(el["height"] * SCALE)
            cx = x + w // 2
            cy = y + h // 2

            points = [(cx, y), (x + w, cy), (cx, y + h), (x, cy)]

            if fill_rgb:
                draw.polygon(points, fill=fill_rgb)
            if stroke_rgb:
                draw.polygon(points, outline=stroke_rgb, width=stroke_width)

        elif el_type == "arrow":
            points = el.get("points", [])
            if len(points) > 1:
                # Draw line segments
                for i in range(len(points) - 1):
                    x1 = transform_x(el["x"] + points[i][0])
                    y1 = transform_y(el["y"] + points[i][1])
                    x2 = transform_x(el["x"] + points[i + 1][0])
                    y2 = transform_y(el["y"] + points[i + 1][1])

                    if stroke_rgb:
                        draw.line([x1, y1, x2, y2], fill=stroke_rgb, width=stroke_width)

                # Draw arrowhead
                if el.get("endArrowhead") == "arrow" and len(points) > 1:
                    last = points[-1]
                    prev = points[-2]

                    x1 = transform_x(el["x"] + last[0])
                    y1 = transform_y(el["y"] + last[1])

                    angle = math.atan2(last[1] - prev[1], last[0] - prev[0])
                    arrow_size = 10 * SCALE

                    # Left arrow line
                    x2 = x1 - arrow_size * math.cos(angle - math.pi / 6)
                    y2 = y1 - arrow_size * math.sin(angle - math.pi / 6)
                    draw.line([x1, y1, x2, y2], fill=stroke_rgb, width=stroke_width)

                    # Right arrow line
                    x3 = x1 - arrow_size * math.cos(angle + math.pi / 6)
                    y3 = y1 - arrow_size * math.sin(angle + math.pi / 6)
                    draw.line([x1, y1, x3, y3], fill=stroke_rgb, width=stroke_width)

        elif el_type == "text":
            text = el.get("text", "")
            font_size = el.get("fontSize", 16)
            font = get_font(font_size)

            lines = text.split("\n")
            line_height = int(font_size * el.get("lineHeight", 1.25) * SCALE)

            for i, line in enumerate(lines):
                text_y = y + i * line_height

                # Text color
                text_color = hex_to_rgb(stroke_color)

                # Draw text
                draw.text((x, text_y), line, fill=text_color, font=font)

    print(f"Saving PNG to: {OUTPUT_PNG}")
    img.save(OUTPUT_PNG, "PNG", optimize=True)
    print("✓ PNG exported successfully!")
    print(
        f"  Dimensions: {width}x{height} px ({width // SCALE}x{height // SCALE} logical)"
    )


if __name__ == "__main__":
    try:
        render_excalidraw_to_png()
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
