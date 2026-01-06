import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from woodster_jigsaw_solver.vision import (
    contour_to_puzzle_piece,
    find_contour_angle,
    find_unit_length,
    rotate_contour,
    scan_puzzle_piece_contours,
)
from woodster_jigsaw_solver.vision.contour_visualization import draw_contour


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect puzzle piece contours and save debug images"
    )
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument(
        "--debug-dir",
        default="debug/contours",
        help="Directory to save debug contour images",
    )
    parser.add_argument(
        "--min-area", type=int, default=100, help="Minimum contour area in pixels"
    )
    parser.add_argument(
        "--blur-kernel", type=int, nargs=2, default=[5, 5], help="Blur kernel size"
    )
    parser.add_argument(
        "--canny-low", type=int, default=50, help="Canny lower threshold"
    )
    parser.add_argument(
        "--canny-high", type=int, default=150, help="Canny upper threshold"
    )

    args = parser.parse_args()

    contours = scan_puzzle_piece_contours(
        args.image_path,
        min_area=args.min_area,
        blur_kernel=tuple(args.blur_kernel),
        canny_threshold1=args.canny_low,
        canny_threshold2=args.canny_high,
    )

    debug_dir = Path(args.debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(contours)} puzzle piece contours")

    if len(contours) < 3:
        raise ValueError("Need at least 3 contours to compute unit length")

    unit_lengths = sorted([find_unit_length(contour) for contour in contours])
    unit_length = sum(unit_lengths[1:-1]) / (len(contours) - 2)

    for i, contour in enumerate(contours, 1):
        angle = find_contour_angle(contour)
        rotated_contour = rotate_contour(contour, -angle)

        contour_img = draw_contour(rotated_contour, color=(0, 255, 0), padding=0)
        piece = contour_to_puzzle_piece(rotated_contour, unit_length)
        print(f"PuzzlePiece {i}:")
        print(piece.ascii_diagram())
        print()

        output_path = debug_dir / f"contour_{i:03d}.png"
        cv2.imwrite(str(output_path), contour_img)
        print(f"Saved contour {i} to {output_path}")


if __name__ == "__main__":
    main()
