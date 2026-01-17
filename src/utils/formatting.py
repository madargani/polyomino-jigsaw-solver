"""Formatting utilities for the puzzle solver application."""

from __future__ import annotations

import hashlib


def generate_unique_color(piece_id: str) -> str:
    """Generate a unique, consistent color for a piece based on its ID.

    Args:
        piece_id: Unique identifier for the piece

    Returns:
        Hex color string (e.g., "#FF5733")
    """
    # Use MD5 hash of piece_id for consistent color generation
    hash_bytes = hashlib.md5(piece_id.encode()).digest()
    # Use first 3 bytes for RGB values
    r, g, b = hash_bytes[0], hash_bytes[1], hash_bytes[2]
    # Ensure colors are vibrant (avoid too dark)
    r = max(r, 100)
    g = max(g, 100)
    b = max(b, 100)
    return f"#{r:02X}{g:02X}{b:02X}"


def get_contrasting_text_color(background_color: str) -> str:
    """Get black or white text color based on background brightness.

    Args:
        background_color: Hex color string (e.g., "#FF5733")

    Returns:
        "#000000" for dark backgrounds, "#FFFFFF" for light backgrounds
    """
    # Remove # if present
    color = background_color.lstrip("#")
    # Parse RGB values
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    # Calculate relative luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"


def format_board_dimensions(width: int, height: int) -> str:
    """Format board dimensions as a string.

    Args:
        width: Board width in cells
        height: Board height in cells

    Returns:
        Formatted string like "5×5"
    """
    return f"{width}×{height}"


def format_piece_count(count: int) -> str:
    """Format piece count with proper pluralization.

    Args:
        count: Number of pieces

    Returns:
        Formatted string like "3 pieces" or "1 piece"
    """
    if count == 1:
        return "1 piece"
    return f"{count} pieces"


def format_area_comparison(piece_area: int, board_area: int) -> str:
    """Format area comparison string.

    Args:
        piece_area: Total area of all pieces
        board_area: Available board area

    Returns:
        Formatted string like "8 / 25 cells"
    """
    return f"{piece_area} / {board_area} cells"


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text with ellipsis if too long.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with "..." if needed
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
