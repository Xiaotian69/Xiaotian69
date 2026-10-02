# Checked Collage Panel Extractor Skill

一个用于 **“蓝色打勾选图 → 从无标记原图精确拆分 → 1:1 输出 → 可选高清增强 → 批量打包”** 的可复用 Agent Skill + Python 工具。

The key idea is simple: **use the marked collage only to determine selection, and always crop final pixels from the matching clean collage.** This prevents the common failure mode where an image model “recreates” a panel instead of actually extracting it.

## Why this exists

When a contact sheet contains many visually similar panels, a user may mark the ones they want with a bright blue/cyan check mark. A good workflow should:

- identify the checked cells;
- find the same cells in the clean version;
- crop, not redraw;
- remove contact-sheet gutters;
- normalize each output to 1:1;
- optionally upscale/sharpen low-resolution crops;
- verify the requested count;
- export individual images and a ZIP.

## Files

- `SKILL.md` — reusable agent instructions.
- `extract_checked_panels.py` — deterministic Pillow/NumPy implementation.
- `requirements.txt` — minimal dependencies.
- `examples/manifest.example.json` — batch-processing example.
- `LICENSE` — MIT.

## Quick start

```bash
pip install -r requirements.txt
```

Single marked/clean pair:

```bash
python extract_checked_panels.py \
  --marked marked.jpg \
  --clean clean.png \
  --rows 2 \
  --cols 3 \
  --out output
```

Require an exact number of selected panels:

```bash
python extract_checked_panels.py \
  --marked marked.jpg \
  --clean clean.png \
  --rows 2 \
  --cols 3 \
  --out output \
  --expected 5
```

Batch mode:

```bash
python extract_checked_panels.py \
  --manifest examples/manifest.example.json \
  --out output \
  --expected 11 \
  --zip
```

## How detection works

The tool does **not** simply search for blue pixels. Artwork itself may contain lots of blue.

Instead it:

1. aligns the marked image to the clean image size;
2. calculates the pixel difference;
3. keeps pixels that are both strongly different **and** cyan/blue in the marked version;
4. counts that mask inside every grid cell;
5. crops selected cells from the clean version.

This makes it well suited to manually annotated contact sheets.

## Output policy

The tool is deliberately non-generative. It will not invent missing details.

Optional `--upscale 2` or `--upscale 4` uses high-quality Lanczos resampling plus restrained sharpening. For genuinely tiny sources, an AI image-restoration model can be used later, but that should be a separate fidelity-preserving step.

## Use as an Agent Skill

Copy the folder into the skill location used by your agent/client, or use `SKILL.md` as the reusable workflow instruction.

The skill is tool-agnostic: it works well with ChatGPT/Work-style agents, coding agents, and local automation setups as long as they can read images and run Python or an equivalent image editor.

## Design principles

- **Extract, don’t regenerate.**
- **Clean source wins.**
- **Minimal crop, maximum fidelity.**
- **Count before delivery.**
- **Generative restoration is a fallback, not the default.**

## License

MIT — free to use, modify, and redistribute.
