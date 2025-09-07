#!/usr/bin/env python3
"""
Batch process script for all files in input directory with optional output directory.

Usage:
  python3 src/scripts/batch_process.py --skip-existing
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Process files in bulk.")
    p.add_argument(
        "--input-dir",
        default=".",
        help="Folder containing input files (tilde ok).",
    )
    p.add_argument(
        "--file-extension",
        default="*",
        help="File extension to process (default: '*').",
    )
    # Default output folder is ./output
    # This is to avoid accidental overwrites if user runs from source folder.
    # User can always specify --output-dir . to write to current folder.
    # Also, we create the output folder if it doesn't exist.
    # out_dir.mkdir(parents=True, exist_ok=True)

    p.add_argument(
        "--output-dir",
        default="./output",
        help="Folder to write output files into (tilde ok).",
    )
    p.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subfolders.",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip conversion if the target output file already exists.",
    )
    # Note: No default here, to force user to think about it.
    # This script is useless without a converter.
    p.add_argument(
        "--converter",
        help="Path to your converter script.",
    )
    ns = p.parse_args(argv)

    in_dir = Path(ns.input_dir).expanduser()
    file_extension = ns.file_extension
    out_dir = Path(ns.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        print(f"Input directory not found: {in_dir}", file=sys.stderr)
        return 2

    file_iter = (
        in_dir.rglob("*." + file_extension)
        if ns.recursive
        else in_dir.glob("*." + file_extension)
    )
    files = sorted(file_iter)
    if not files:
        print(f"No files found in {in_dir}", file=sys.stderr)
        return 1

    ok = 0
    fail = 0

    for file_path in files:
        output_xlsx = out_dir / (file_path.stem + ".xlsx")

        if ns.skip_existing and output_xlsx.exists():
            print(f"↷ Skipping (exists): {output_xlsx}")
            continue

        print(f"→ Converting {file_path} → {output_xlsx}")
        try:
            # Call your converter with safe args (no shell quoting woes).
            subprocess.run(
                [sys.executable, ns.converter, str(file_path), str(output_xlsx)],
                check=True,
            )
            ok += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ FAILED for {file_path}: {e}", file=sys.stderr)
            fail += 1

    print(f"\nDone. {ok} succeeded, {fail} failed.")
    return 0 if fail == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
