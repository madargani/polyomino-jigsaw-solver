"""Color generation utility for polyomino pieces."""

from __future__ import annotations

import colorsys

from PySide6.QtGui import QColor


def _qcolor_to_hsv(color: QColor) -> tuple[int, int, int, int]:
    """Convert QColor to HSV tuple (h, s, v, a).

    Args:
        color: The QColor to convert

    Returns:
        Tuple of (hue, saturation, value, alpha) where h, s, v, a are 0-255
    """
    r = color.red() / 255.0
    g = color.green() / 255.0
    b = color.blue() / 255.0
    a = color.alpha()

    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (int(h * 255), int(s * 255), int(v * 255), a)


def _hsv_to_qcolor(h: int, s: int, v: int, a: int = 255) -> QColor:
    """Convert HSV values to QColor.

    Args:
        h: Hue (0-255)
        s: Saturation (0-255)
        v: Value (0-255)
        a: Alpha (0-255)

    Returns:
        QColor object
    """
    r, g, b = colorsys.hsv_to_rgb(h / 255.0, s / 255.0, v / 255.0)
    return QColor.fromRgb(int(r * 255), int(g * 255), int(b * 255), a)


# Predefined palette of visually distinct colors optimized for piece visualization
# These colors are chosen to be distinct from each other while maintaining
# good contrast against both light and dark backgrounds
_PIECE_COLORS = [
    # Vibrant, saturated colors that stand out well
    QColor(220, 53, 69),  # Red
    QColor(0, 123, 255),  # Blue
    QColor(40, 167, 69),  # Green
    QColor(255, 193, 7),  # Yellow
    QColor(111, 66, 193),  # Purple
    QColor(23, 162, 184),  # Cyan
    QColor(253, 126, 20),  # Orange
    QColor(108, 117, 125),  # Gray
    QColor(134, 142, 150),  # Light Gray
    QColor(52, 58, 64),  # Dark Gray
    QColor(206, 212, 218),  # Very Light Gray
    QColor(255, 0, 255),  # Magenta
    QColor(0, 255, 255),  # Cyan
    QColor(128, 0, 128),  # Purple
    QColor(255, 165, 0),  # Orange
    QColor(70, 130, 180),  # Steel Blue
    QColor(60, 179, 113),  # Medium Sea Green
    QColor(255, 105, 180),  # Hot Pink
    QColor(0, 206, 209),  # Dark Turquoise
    QColor(148, 0, 211),  # Dark Violet
    QColor(255, 127, 80),  # Coral
    QColor(64, 224, 208),  # Turquoise
    QColor(186, 85, 211),  # Medium Orchid
    QColor(50, 205, 50),  # Lime Green
    QColor(255, 69, 0),  # Red-Orange
    QColor(138, 43, 226),  # Blue Violet
    QColor(30, 144, 255),  # Dodger Blue
    QColor(255, 215, 0),  # Gold
    QColor(220, 20, 60),  # Crimson
    QColor(0, 191, 255),  # Deep Sky Blue
    QColor(154, 205, 50),  # Yellow Green
    QColor(255, 20, 147),  # Deep Pink
    QColor(0, 255, 127),  # Spring Green
    QColor(255, 99, 71),  # Tomato
    QColor(147, 112, 219),  # Medium Purple
    QColor(72, 209, 204),  # Medium Turquoise
    QColor(255, 228, 181),  # Moccasin
    QColor(255, 218, 185),  # Peach Puff
    QColor(186, 220, 88),  # Light Green
    QColor(255, 183, 178),  # Light Coral
    QColor(174, 218, 227),  # Light Blue
    QColor(218, 165, 32),  # Goldenrod
    QColor(188, 143, 143),  # Rosy Brown
    QColor(143, 188, 143),  # Dark Sea Green
    QColor(255, 160, 122),  # Salmon
    QColor(100, 149, 237),  # Cornflower Blue
    QColor(240, 128, 128),  # Light Coral
    QColor(173, 216, 230),  # Light Blue
    QColor(144, 238, 144),  # Light Green
    QColor(255, 182, 193),  # Light Pink
    QColor(255, 218, 185),  # Peach
    QColor(221, 160, 221),  # Plum
    QColor(176, 224, 230),  # Powder Blue
    QColor(255, 228, 196),  # Bisque
    QColor(250, 128, 114),  # Salmon
    QColor(255, 250, 205),  # Lemon Chiffon
    QColor(240, 230, 140),  # Khaki
    QColor(230, 190, 120),  # Sandy Brown
    QColor(255, 200, 150),  # Light Orange
    QColor(200, 230, 200),  # Pale Green
    QColor(180, 200, 255),  # Pale Blue
    QColor(255, 220, 220),  # Pale Pink
    QColor(220, 220, 180),  # Pale Yellow
]


def get_piece_color(piece_index: int) -> QColor:
    """Get a distinct color for a piece based on its index.

    Args:
        piece_index: The index of the piece (0-based)

    Returns:
        A QColor that is visually distinct from other piece colors
    """
    if piece_index < 0:
        raise ValueError("Piece index cannot be negative")

    # Use modulo to cycle through colors if we have more pieces than colors
    return _PIECE_COLORS[piece_index % len(_PIECE_COLORS)]


def get_dark_variant(color: QColor) -> QColor:
    """Create a darker variant of a color for borders and contrast.

    Args:
        color: The original QColor

    Returns:
        A darker variant of the color
    """
    h, s, v, a = _qcolor_to_hsv(color)
    new_v = max(0, v - 40)
    return _hsv_to_qcolor(h, s, new_v, a)


def get_light_variant(color: QColor, alpha: int = 50) -> QColor:
    """Create a lighter, more transparent variant of a color for highlights.

    Args:
        color: The original QColor
        alpha: The alpha value for the light variant (0-255)

    Returns:
        A lighter, more transparent variant of the color
    """
    h, s, v, _ = _qcolor_to_hsv(color)
    new_v = min(255, v + 40)
    return _hsv_to_qcolor(h, s, new_v, alpha)


def generate_color_sequence(count: int) -> list[QColor]:
    """Generate a sequence of distinct colors.

    Args:
        count: Number of colors to generate

    Returns:
        List of distinct QColor objects
    """
    if count <= 0:
        return []

    colors = []
    for i in range(count):
        colors.append(get_piece_color(i))
    return colors
