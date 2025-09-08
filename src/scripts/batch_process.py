#!/usr/bin/env python3
"""
Batch process all files in input directory with Python script optional output directory.

Usage:
  python3 src/scripts/batch_process.py \
    -i ./input               # Input folder (optional, default .)
    -o ./output              # Output folder (optional, default ./output)
    -s                       # Skip existing output files
    --file-extension png     # File extension to process (optional, default '*')
    ./path/to/your_script.py # Your Python python_script script
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Process files in bulk.")
    # This script is useless without a Python executable.
    p.add_argument(
        "python_script",
        help="Path to your Python executable.",
    )
    p.add_argument(
        "-i",
        "--input-dir",
        default=".",
        help="Folder containing input files (tilde ok).",
    )
    # Default output folder is ./output
    # This is to avoid accidental overwrites if user runs from source folder.
    # User can always specify --output-dir . to write to current folder.
    # Also, we create the output folder if it doesn't exist.
    # out_dir.mkdir(parents=True, exist_ok=True)

    p.add_argument(
        "-o",
        "--output-dir",
        default="./output",
        help="Folder to write output files into (tilde ok).",
    )
    p.add_argument(
        "--file-extension",
        default="*",
        help="File extension to process (default: '*').",
    )
    p.add_argument(
        "-s",
        "--skip-existing",
        action="store_true",
        help="Skip conversion if the target output file already exists.",
    )
    ns = p.parse_args(argv)

    python_script = ns.python_script
    in_dir = Path(ns.input_dir).expanduser()
    out_dir = Path(ns.output_dir).expanduser()
    file_extension = ns.file_extension
    skip_existing = ns.skip_existing

    if not in_dir.exists():
        print(f"Input directory not found: {in_dir}", file=sys.stderr)
        return 2

    file_iter = in_dir.glob("*." + file_extension)
    files = sorted(file_iter)
    if not files:
        print(f"No files found in {in_dir}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    fail = 0

    print(f"Processing files in '{in_dir}'\n")
    for file_path in files:
        trying = (
            f"Trying: {ns.python_script} --output-dir {str(out_dir)}"
        )
        if skip_existing:
            trying += " --skip-existing"
        trying += f" {str(file_path)}"
        print(trying)
        try:
            # Call your python_script with safe args (no shell quoting woes).
            run_parameters: list[str] = [
                sys.executable,
                python_script,
                "--output-dir",
                str(out_dir),
            ]

            if skip_existing:
                run_parameters.append("--skip-existing")

            run_parameters.append(str(file_path))

            subprocess.run(
                run_parameters,
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
