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
import re
import sys
import zipfile
from pathlib import Path
from typing import Iterable

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def load_rgb(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGB")


def align_marked_to_clean(marked: Image.Image, clean: Image.Image) -> Image.Image:
    if marked.size == clean.size:
        return marked
    if abs(marked.width / marked.height / (clean.width / clean.height) - 1) > .01:
        raise ValueError("Marked/clean aspect ratios differ; align the sheets first.")
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


def make_square(img: Image.Image, mode: str = "pad") -> Image.Image:
    w, h = img.size
    if mode == "keep" or w == h:
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
    if text is None:
        return None
    out = []
    for item in text.split(";"):
        item = item.strip()
        if not item:
            continue
        r, c = item.split(",")
        out.append((int(r) - 1, int(c) - 1))
    if len(out) != len(set(out)):
        raise ValueError("Manual selections contain duplicate cells.")
    if not out:
        raise ValueError("Manual selections must not be empty.")
    return out




def load_manifest(path: Path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list) or not data:
        raise ValueError("Manifest must be a nonempty JSON array.")

    base = path.parent
    normalized = []
    for i, item in enumerate(data, start=1):
        normalized.append(
            {
                "marked": (base / item["marked"]).resolve() if item.get("marked") else None,
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
    p.add_argument("--square-mode", choices=["crop", "pad", "keep"], default="pad")
    p.add_argument("--trim-white", action="store_true", help="Opt in to white-edge trimming; may remove artwork borders.")
    p.add_argument("--gutter", type=int, default=0, help="Inset each cell edge by this many pixels.")
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
    if args.expected is not None and args.expected < 1:
        raise ValueError("--expected must be positive.")
    if args.gutter < 0 or args.min_pixels < 1 or not 0 < args.min_ratio <= 1 or not 0 < args.diff_threshold <= 255:
        raise ValueError("Invalid gutter or detection threshold.")

    jobs = []

    if args.manifest:
        if args.marked or args.clean or args.manual:
            raise ValueError("Use --manifest or single-pair arguments, not both.")
        jobs = load_manifest(args.manifest)
    else:
        if not args.clean or (not args.marked and args.manual is None):
            print("error: provide --manifest, or --clean with --marked or --manual", file=sys.stderr)
            return 2
        jobs = [
            {
                "marked": args.marked.resolve() if args.marked else None,
                "clean": args.clean.resolve(),
                "rows": args.rows,
                "cols": args.cols,
                "prefix": "sheet01",
                "manual": parse_manual(args.manual),
            }
        ]

    plans, report = [], []
    # Validate the whole batch and count selections before writing anything.
    for job in jobs:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", job["prefix"]):
            raise ValueError("Prefix must contain only letters, numbers, '_' or '-'.")
        clean = load_rgb(job["clean"])
        rows, cols = job["rows"], job["cols"]
        if not 1 <= rows <= clean.height or not 1 <= cols <= clean.width:
            raise ValueError("Grid dimensions must be positive and fit the source.")
        if job["manual"] is None:
            if job["marked"] is None:
                raise ValueError("Each manifest job needs marked or manual.")
            selected, scores = detect_selected_cells(load_rgb(job["marked"]), clean, rows, cols,
                args.min_ratio, args.min_pixels, args.diff_threshold)
        else:
            selected, scores = job["manual"], []
        entry = dict(prefix=job["prefix"], clean=job["clean"].name,
                     marked=job["marked"].name if job["marked"] else None,
                     grid=[rows, cols], scores=[dict(row=r+1, col=c+1, pixels=n, ratio=f)
                                               for r, c, n, f in scores], panels=[])
        for index, (row, col) in enumerate(selected, 1):
            if not (0 <= row < rows and 0 <= col < cols):
                raise ValueError("Manual selection is outside the grid.")
            x0, y0, x1, y1 = grid_box(clean.width, clean.height, rows, cols, row, col)
            box = (x0+args.gutter, y0+args.gutter, x1-args.gutter, y1-args.gutter)
            if box[2] <= box[0] or box[3] <= box[1]:
                raise ValueError("Gutter removes the entire cell.")
            path = args.out / f"{job['prefix']}_{index:02d}_r{row+1}_c{col+1}.png"
            plans.append((clean, box, path))
            entry["panels"].append(dict(row=row+1, col=col+1, box=list(box), output=path.name))
        report.append(entry)
    if args.expected is not None and len(plans) != args.expected:
        print(
            f"error: expected {args.expected} output(s), got {len(plans)}; nothing exported",
            file=sys.stderr,
        )
        return 3
    if not plans:
        print(json.dumps(report, indent=2))
        raise ValueError("No checks detected. Inspect scores or use --manual.")
    all_outputs = [path for _, _, path in plans]
    report_path = args.out / "selection_report.json"
    targets = all_outputs + [report_path]
    if args.make_zip:
        targets.append(args.out / "selected_panels.zip")
    if len({str(p.resolve()).casefold() for p in targets}) != len(targets):
        raise ValueError("Output names collide; use distinct manifest prefixes.")
    for path in targets:
        if path.exists():
            raise ValueError(f"Refusing to overwrite: {path}")
    args.out.mkdir(parents=True, exist_ok=True)
    for clean, box, path in plans:
        crop = clean.crop(box)
        if args.trim_white:
            crop = trim_white_edges(crop)
        crop = enhance(make_square(crop, args.square_mode), args.upscale)
        crop.save(path, "PNG", optimize=True)
    report_path.write_text(json.dumps(dict(count=len(plans), square_mode=args.square_mode,
        upscale=args.upscale, gutter=args.gutter, trim_white=args.trim_white,
        sheets=report), ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"total: {len(all_outputs)} output(s)")
    for p in all_outputs:
        print(p)

    if args.make_zip and all_outputs:
        zip_path = args.out / "selected_panels.zip"
        create_zip(all_outputs + [report_path], zip_path)
        print(zip_path)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
