
#!/usr/bin/env python3
"""
Process file with optional output directory.

Usage:
  python3 src/scripts/process_file.py \
    -o ./output              # Output folder (optional, default ./output)
    -s                       # Skip existing output files
    ./path/to/file_to_process # File to process
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Process file.")
    p.add_argument(
        "input_file",
        help="File to process.",
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
        "-s",
        "--skip-existing",
        action="store_true",
        help="Skip conversion if the target output file already exists.",
    )
    ns = p.parse_args(argv)

    file_to_process = Path(ns.input_file).expanduser()
    out_dir = Path(ns.output_dir).expanduser()
    skip_existing = ns.skip_existing

    if not file_to_process.exists():
        print(f"Error: Input file '{str(file_to_process)}' does not exist.")
        return 1
    if not file_to_process.is_file():
        print(f"Error: Input file '{str(file_to_process)}' is not a file.")
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / file_to_process.name
    if skip_existing and out_file.exists():
        print(f"Skipping existing output file '{str(out_file)}'.")
        return 0
    print(f"Processing file '{str(file_to_process)}'...")
    # Here you would call your processing function, e.g.:
    # process_file(file_to_process, out_file)
    print(f"Output written to '{str(out_file)}'.")


    return 0

if __name__ == "__main__":
    raise SystemExit(main())
