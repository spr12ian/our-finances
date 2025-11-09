#!/usr/bin/env python3
"""
Batch-convert SSACRD statements (PDF) -> XLSX using converter script.

Usage:
  python3 src/scripts/ssacrd_pdfs_to_xlsx.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = (Path("src") / "scripts").resolve()
BATCH_PROCESSOR = SCRIPTS_DIR / "batch_process.py"
FILE_PROCESSOR = SCRIPTS_DIR / "ssacrd_pdf_to_csv.py"

SSACRD_DIR = (
    Path.home()
    / "SSACRD"
)

INPUT_DIR = SSACRD_DIR

OUTPUT_DIR = SSACRD_DIR


def main() -> int:
    if not FILE_PROCESSOR.exists():
        print(f"File processor not found: {FILE_PROCESSOR}", file=sys.stderr)
        return 2

    if not INPUT_DIR.exists():
        print(f"Input directory not found: {INPUT_DIR}", file=sys.stderr)
        return 2

    print(f"→ Converting .pdf files in {INPUT_DIR} → {OUTPUT_DIR} .xlsx files")
    try:
        # Call your converter with safe args (no shell quoting woes).
        run_parameters = [
            sys.executable,
            str(BATCH_PROCESSOR),
            str(FILE_PROCESSOR),
            "-i",
            str(INPUT_DIR),
            "-o",
            str(OUTPUT_DIR),
            "-s",
        ]
        subprocess.run(
            run_parameters,
            check=True,
        )

    except subprocess.CalledProcessError as e:
        print(f"✗ FAILED for {FILE_PROCESSOR}: {e}", file=sys.stderr)

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
