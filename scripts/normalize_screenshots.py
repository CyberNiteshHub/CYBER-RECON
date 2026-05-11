#!/usr/bin/env python3
"""
Rename PNG files in screenshots/ to ui-01.png, ui-02.png, … (sorted by current name).

Uses pathlib + shutil only (safe for spaces in filenames). Keeps README.md and
other non-PNG files untouched. Idempotent if you only have ui-*.png left.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOT = ROOT / "screenshots"
TMP = SHOT / "_renaming_tmp"


def main() -> int:
    if not SHOT.is_dir():
        print(f"Missing folder: {SHOT}", file=sys.stderr)
        return 1

    if TMP.exists():
        shutil.rmtree(TMP)

    pngs = sorted(
        p.name
        for p in SHOT.iterdir()
        if p.is_file() and p.suffix.lower() == ".png" and not p.name.startswith("_")
    )
    if not pngs:
        print(f"No PNG files in {SHOT}")
        return 0

    TMP.mkdir(parents=True, exist_ok=True)
    for name in pngs:
        shutil.move(str(SHOT / name), str(TMP / name))

    for i, name in enumerate(sorted(TMP.iterdir(), key=lambda p: p.name), 1):
        shutil.move(str(name), str(SHOT / f"ui-{i:02d}.png"))

    TMP.rmdir()
    print(f"OK: {len(pngs)} screenshots → ui-01.png … ui-{len(pngs):02d}.png in {SHOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
