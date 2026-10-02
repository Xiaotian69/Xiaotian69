---
name: checked-collage-panel-extractor
description: Extract panels marked with bright blue/cyan check marks from contact sheets, using the matching clean contact sheets as the source. Preserve the selected artwork exactly, normalize outputs to 1:1, optionally enhance low-resolution crops, verify the requested count, and package the results.
---

# Checked Collage Panel Extractor

## When to use

Use this skill when a user provides one or more collage/contact-sheet images with blue or cyan check marks and wants the checked panels exported as separate images.

Typical requests:
- “把我打勾的图单独拆出来”
- “根据蓝色对勾选图”
- “不要重新生成，直接从干净版里裁出来”
- “每张 1:1，模糊的话高清修复，最后打包”

## Inputs

Prefer two matched sets:

1. **Marked sheets** — used only to identify which panels were selected.
2. **Clean sheets** — the same layouts without check marks; these are the pixel source for final crops.

Optional:
- expected output count;
- grid shape, e.g. 2 rows × 3 columns;
- desired final size;
- whether generative restoration is allowed.

## Non-negotiable rules

1. **Never use the marked sheet as the final crop when a clean counterpart exists.**
2. **Do not redraw or regenerate a selected panel just because extraction is inconvenient.**
3. Use the marked sheet only as a selection mask; crop the corresponding region from the clean sheet.
4. Preserve the original composition, decorative insets, texture, color, grain, borders internal to the artwork, and relative placement.
5. Remove only contact-sheet gutters, check marks, and accidental outer whitespace.
6. Output each selected panel as **1:1**.
7. Prefer deterministic restoration first: high-quality resampling, mild denoise, and restrained sharpening.
8. Use generative restoration only as a fallback when the user asks for it or when the source is genuinely too small to recover non-generatively. If used, keep structure faithful and do not invent new design elements.
9. Verify the final count against the user’s expected count before packaging.
10. Export individual files plus a ZIP when multiple images are requested.

## Workflow

### 1. Pair marked and clean sheets

Match each marked contact sheet with its clean version by layout and artwork identity.

If there are multiple near-duplicates, compare:
- panel positions;
- major subjects;
- inset thumbnails;
- color blocks;
- crop boundaries.

### 2. Detect selected panels

Best method: compare the marked sheet against its clean counterpart.

The blue/cyan check marks are present only in the marked version, so use:
- image difference;
- a cyan/blue color mask;
- per-cell mask area.

This is more reliable than searching the marked image for “blue” alone because the artwork itself may contain blue regions.

### 3. Map selections to grid cells

For regular contact sheets, divide by known rows and columns.

If separator gutters are visible, use them to refine boundaries. Do not let a few pixels of white gutter become part of the final image.

### 4. Crop from the clean sheet

For every selected cell:
- crop the same region from the clean counterpart;
- trim only outer gutter/whitespace;
- preserve all content inside the panel.

### 5. Normalize to 1:1

Preferred order:
1. trim separator gutters;
2. if the panel is already approximately square, make only a minimal center crop;
3. if a meaningful subject would be cut, pad instead of aggressively cropping.

Never stretch the image non-uniformly.

### 6. Restore only when needed

Default non-generative enhancement:
- Lanczos upscale;
- mild sharpening;
- optional light denoise.

Avoid aggressive sharpening that creates halos.

For AI restoration:
- retain the original crop as the visual reference;
- do not alter subject identity, pose, ornament, insets, typography, color blocks, or layout;
- treat restoration as fidelity work, not redesign.

### 7. QA

Before delivery, check:
- selection count;
- no check marks remain;
- no wrong cells;
- no duplicate outputs;
- 1:1 aspect ratio;
- no leftover contact-sheet gutters;
- correct orientation;
- no missing inset details;
- filenames are ordered and stable.

### 8. Package

Recommended naming:

```text
01_r1_c1.png
02_r1_c2.png
03_r1_c3.png
...
```

Then create:

```text
selected_panels.zip
```

## Tool strategy

- **Pixel-exact extraction:** Python + Pillow/NumPy, ImageMagick, Photoshop, or equivalent.
- **Visual selection review:** built-in vision or image editor.
- **Restoration:** deterministic resize/sharpen first; image generation/editing only when necessary.
- **Packaging:** ZIP the final individual files.

## Reference implementation

This repository includes `extract_checked_panels.py`, which detects cyan/blue check marks by differencing a marked sheet against its clean counterpart and exports the corresponding clean cells.

The script is intentionally conservative: it extracts existing pixels and does not use generative AI.
