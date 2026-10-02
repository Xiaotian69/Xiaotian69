#!/usr/bin/env python3
"""
Checked Collage Panel Extractor

Detect bright cyan/blue check marks by comparing a marked contact sheet
against a matching clean sheet, then crop selected cells from the clean sheet.

Dependencies: Pillow, NumPy
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageFilter


def load_rgb(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB")


def align_marked_to_clean(marked: Image.Image, clean: Image.Image) -> Image.Image:
    if marked.size == clean.size:
        return marked
    return marked.resize(clean.size, Image.Resampling.LANCZOS)


def blue_check_mask(
    marked: Image.Image,
    clean: Image.Image,
    diff_threshold: float = 55.0,
) -> np.ndarray:
    """Return a boolean mask for bright cyan/blue annotation pixels.

    We require BOTH:
      1) a strong difference from the clean image, and
      2) a cyan/blue-looking pixel in the marked image.

    This suppresses blue artwork that exists in both images.
    """
    marked = align_marked_to_clean(marked, clean)
    m = np.asarray(marked, dtype=np.int16)
    c = np.asarray(clean, dtype=np.int16)

    diff = np.abs(m - c).mean(axis=2)

    r = m[:, :, 0]
    g = m[:, :, 1]
    b = m[:, :, 2]

    cyan_blue = (
        (b >= 150)
        & (g >= 110)
        & (r <= 130)
        & ((b - r) >= 60)
        & ((g - r) >= 35)
    )

    return (diff >= diff_threshold) & cyan_blue


def grid_box(width: int, height: int, rows: int, cols: int, row: int, col: int):
    x0 = round(col * width / cols)
    x1 = round((col + 1) * width / cols)
    y0 = round(row * height / rows)
    y1 = round((row + 1) * height / rows)
    return x0, y0, x1, y1


def trim_white_edges(img: Image.Image, max_fraction: float = 0.06) -> Image.Image:
    """Trim only thin, nearly-white separator bands from the outside."""
    a = np.asarray(img.convert("RGB"))
    h, w, _ = a.shape

    max_x = max(1, int(w * max_fraction))
    max_y = max(1, int(h * max_fraction))

    def white_line(line: np.ndarray) -> bool:
        bright = np.all(line >= 238, axis=1)
        return float(bright.mean()) >= 0.88

    left = 0
    while left < max_x and white_line(a[:, left, :]):
        left += 1

    right = w
    trimmed = 0
    while trimmed < max_x and right > left and white_line(a[:, right - 1, :]):
        right -= 1
        trimmed += 1

    top = 0
    while top < max_y and white_line(a[top, :, :]):
        top += 1

    bottom = h
    trimmed = 0
    while trimmed < max_y and bottom > top and white_line(a[bottom - 1, :, :]):
        bottom -= 1
        trimmed += 1

    if right - left < 8 or bottom - top < 8:
        return img

    return img.crop((left, top, right, bottom))


def make_square(img: Image.Image, mode: str = "crop") -> Image.Image:
    w, h = img.size
    if w == h:
        return img

    if mode == "pad":
        side = max(w, h)
        canvas = Image.new("RGB", (side, side), (255, 255, 255))
        canvas.paste(img, ((side - w) // 2, (side - h) // 2))
        return canvas

    side = min(w, h)
    x0 = (w - side) // 2
    y0 = (h - side) // 2
    return img.crop((x0, y0, x0 + side, y0 + side))


def enhance(img: Image.Image, upscale: int) -> Image.Image:
    if upscale <= 1:
        return img

    w, h = img.size
    out = img.resize((w * upscale, h * upscale), Image.Resampling.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius=1.2, percent=115, threshold=3))
    return out


def detect_selected_cells(
    marked: Image.Image,
    clean: Image.Image,
    rows: int,
    cols: int,
    min_ratio: float = 0.0012,
    min_pixels: int = 100,
    diff_threshold: float = 55.0,
):
    mask = blue_check_mask(marked, clean, diff_threshold=diff_threshold)
    h, w = mask.shape

    selected = []
    scores = []

    for r in range(rows):
        for c in range(cols):
            x0, y0, x1, y1 = grid_box(w, h, rows, cols, r, c)
            cell = mask[y0:y1, x0:x1]
            count = int(cell.sum())
            area = max(1, cell.size)
            ratio = count / area
            scores.append((r, c, count, ratio))
            if count >= min_pixels and ratio >= min_ratio:
                selected.append((r, c))

    return selected, scores


def parse_manual(text: str | None):
    if not text:
        return None
    out = []
    for item in text.split(";"):
        item = item.strip()
        if not item:
            continue
        r, c = item.split(",")
        out.append((int(r) - 1, int(c) - 1))
    return out


def export_pair(
    marked_path: Path,
    clean_path: Path,
    rows: int,
    cols: int,
    out_dir: Path,
    prefix: str,
    upscale: int,
    square_mode: str,
    manual: list[tuple[int, int]] | None,
    diff_threshold: float,
    min_ratio: float,
    min_pixels: int,
):
    marked = load_rgb(marked_path)
    clean = load_rgb(clean_path)

    if manual is None:
        selected, scores = detect_selected_cells(
            marked,
            clean,
            rows,
            cols,
            min_ratio=min_ratio,
            min_pixels=min_pixels,
            diff_threshold=diff_threshold,
        )
    else:
        selected = manual
        scores = []

    outputs = []
    for idx, (r, c) in enumerate(selected, start=1):
        x0, y0, x1, y1 = grid_box(clean.width, clean.height, rows, cols, r, c)
        crop = clean.crop((x0, y0, x1, y1))
        crop = trim_white_edges(crop)
        crop = make_square(crop, mode=square_mode)
        crop = enhance(crop, upscale)

        filename = f"{prefix}_{idx:02d}_r{r+1}_c{c+1}.png"
        path = out_dir / filename
        crop.save(path, "PNG", optimize=True)
        outputs.append(path)

    return outputs, scores


def load_manifest(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Manifest must be a JSON array.")

    base = path.parent
    normalized = []
    for i, item in enumerate(data, start=1):
        normalized.append(
            {
                "marked": (base / item["marked"]).resolve(),
                "clean": (base / item["clean"]).resolve(),
                "rows": int(item.get("rows", 2)),
                "cols": int(item.get("cols", 3)),
                "prefix": str(item.get("prefix", f"sheet{i:02d}")),
                "manual": parse_manual(item.get("manual")),
            }
        )
    return normalized


def create_zip(paths: Iterable[Path], zip_path: Path):
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=p.name)


def build_parser():
    p = argparse.ArgumentParser(
        description="Extract blue-check-marked collage cells from the matching clean sheet."
    )

    p.add_argument("--marked", type=Path)
    p.add_argument("--clean", type=Path)
    p.add_argument("--rows", type=int, default=2)
    p.add_argument("--cols", type=int, default=3)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--out", type=Path, default=Path("output"))
    p.add_argument("--expected", type=int)
    p.add_argument("--upscale", type=int, choices=[1, 2, 3, 4], default=1)
    p.add_argument("--square-mode", choices=["crop", "pad"], default="crop")
    p.add_argument(
        "--manual",
        help='Manual 1-based selections, e.g. "1,1;1,2;2,3". Overrides detection.',
    )
    p.add_argument("--diff-threshold", type=float, default=55.0)
    p.add_argument("--min-ratio", type=float, default=0.0012)
    p.add_argument("--min-pixels", type=int, default=100)
    p.add_argument("--zip", action="store_true", dest="make_zip")

    return p


def main():
    args = build_parser().parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    jobs = []

    if args.manifest:
        jobs = load_manifest(args.manifest)
    else:
        if not args.marked or not args.clean:
            print("error: provide --manifest or both --marked and --clean", file=sys.stderr)
            return 2
        jobs = [
            {
                "marked": args.marked.resolve(),
                "clean": args.clean.resolve(),
                "rows": args.rows,
                "cols": args.cols,
                "prefix": "sheet01",
                "manual": parse_manual(args.manual),
            }
        ]

    all_outputs = []

    for job in jobs:
        if not job["marked"].exists():
            raise FileNotFoundError(job["marked"])
        if not job["clean"].exists():
            raise FileNotFoundError(job["clean"])

        outputs, scores = export_pair(
            marked_path=job["marked"],
            clean_path=job["clean"],
            rows=job["rows"],
            cols=job["cols"],
            out_dir=args.out,
            prefix=job["prefix"],
            upscale=args.upscale,
            square_mode=args.square_mode,
            manual=job["manual"],
            diff_threshold=args.diff_threshold,
            min_ratio=args.min_ratio,
            min_pixels=args.min_pixels,
        )

        all_outputs.extend(outputs)

        print(f"{job['prefix']}: selected {len(outputs)} panel(s)")
        if not outputs and scores:
            print("  No checks detected. Cell mask scores:")
            for r, c, count, ratio in scores:
                print(f"  r{r+1} c{c+1}: pixels={count}, ratio={ratio:.6f}")

    if args.expected is not None and len(all_outputs) != args.expected:
        print(
            f"error: expected {args.expected} output(s), got {len(all_outputs)}",
            file=sys.stderr,
        )
        return 3

    print(f"total: {len(all_outputs)} output(s)")
    for p in all_outputs:
        print(p)

    if args.make_zip and all_outputs:
        zip_path = args.out / "selected_panels.zip"
        create_zip(all_outputs, zip_path)
        print(zip_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
