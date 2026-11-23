#!/usr/bin/env python3
"""main.py — make.fun news-image-20261123 entry point.

Run with no network access. Generates app/entry.png (if not present) and copies it
to $MAKEFUN_OUTPUT_DIR/app/entry.png (or /output/entry.png) for the competition sandbox.
"""
import os
import shutil

APP_PNG  = os.path.join(os.path.dirname(__file__), "app", "entry.png")
OUT_DIR  = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUT_PATH = os.path.join(OUT_DIR, "app", "entry.png")

def main():
    if not os.path.exists(APP_PNG):
        print("app/entry.png not found — generating now...")
        import draw_entry   # noqa: F401
    else:
        print(f"Found existing {APP_PNG} — skipping generation.")

    assert os.path.exists(APP_PNG), f"{APP_PNG} does not exist after generation step"
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    shutil.copy2(APP_PNG, OUT_PATH)
    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"Copied entry to {OUT_PATH}  ({size_kb:.1f} KiB)")

if __name__ == "__main__":
    main()
