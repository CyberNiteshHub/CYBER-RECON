#!/usr/bin/env python3
"""Rename all PNG files in ../screenshots to ui-01.png, ui-02.png, ... (sorted by name)."""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = os.path.join(ROOT, "screenshots")
TMP = os.path.join(SHOT, "_renaming_tmp")


def main():
    if not os.path.isdir(SHOT):
        print(f"Missing folder: {SHOT}")
        return 1
    files = []
    for name in os.listdir(SHOT):
        if name.endswith(".png") and not name.startswith("_"):
            files.append(name)
    files.sort()
    if not files:
        print(f"No PNG files in {SHOT}")
        return 0
    os.makedirs(TMP, exist_ok=True)
    for name in files:
        shutil.move(os.path.join(SHOT, name), os.path.join(TMP, name))
    for i, name in enumerate(sorted(os.listdir(TMP)), 1):
        shutil.move(os.path.join(TMP, name), os.path.join(SHOT, f"ui-{i:02d}.png"))
    os.rmdir(TMP)
    print(f"Renamed {len(files)} screenshots under {SHOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
