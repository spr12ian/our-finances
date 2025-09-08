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
import os
import shutil
import subprocess
import sys
from pathlib import Path

if shutil.which("hatch") is None:
    print(
        "Error: 'hatch' not found in PATH. Install Hatch or add it to PATH.",
        file=sys.stderr,
    )
    sys.exit(2)


def _looks_like_path(s: str) -> bool:
    # Treat as a path if it ends with .py or contains a path separator
    return (
        s.endswith(".py") or (os.sep in s) or (os.altsep is not None and os.altsep in s)
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Process files in bulk via Hatch.")
    # This script is useless without a Python executable.
    p.add_argument(
        "target",
        help=(
            "Hatch script name (from [tool.hatch.scripts]) "
            "OR path to a Python script (e.g., src/scripts/foo.py)."
        ),
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

    target = ns.target
    in_dir = Path(ns.input_dir).expanduser()
    out_dir = Path(ns.output_dir).expanduser()
    file_extension = ns.file_extension
    skip_existing = ns.skip_existing

    if not in_dir.exists():
        print(f"Input directory not found: {in_dir}", file=sys.stderr)
        return 2

    if file_extension == "*":
        files = sorted(in_dir.glob("*"))
    else:
        files = sorted(in_dir.glob(f"*.{file_extension}")) + sorted(
            in_dir.glob(f"*.{file_extension.upper()}")
        )

    if not files:
        print(f"No files found in {in_dir}", file=sys.stderr)
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    fail = 0

    print(f"Processing files in '{in_dir}' via Hatch\n")

    hatch_prefix: list[str] = ["hatch", "run"]

    # Decide whether target is a hatch script or a python path
    use_path = _looks_like_path(target)
    if use_path:
        target_path = str(Path(target).expanduser())
        base_cmd = hatch_prefix + ["python", target_path, "--"]
    else:
        # Treat as a Hatch script alias from pyproject
        base_cmd = hatch_prefix + [target, "--"]

    for file_path in files:
        cmd = base_cmd + ["--output-dir", str(out_dir)]
        if skip_existing:
            cmd.append("--skip-existing")
        cmd.append(str(file_path))

        print("Trying:", " ".join(cmd))
        try:
            subprocess.run(cmd, check=True)

            ok += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ FAILED for {file_path}: {e}", file=sys.stderr)
            fail += 1
        except KeyboardInterrupt:
            print("\nAborted by user.")
            break

    print(f"\nDone. {ok} succeeded, {fail} failed.")
    return 0 if fail == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
