#!/usr/bin/env python3
"""
Batch-convert SSACRD statements (PDF) -> XLSX using converter script.

Usage:
  python3 src/scripts/ssacrd_pdfs_to_xlsx.py --skip-existing
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Convert PDFs to XLSX in bulk.")
    p.add_argument(
        "--input-dir",
        default="~/data/GoogleDrive/My Drive/People/Ian Sweeney/Financial Transactions/SSACRD (5229 4890 4592 9253)/Statements (PDF)",
        help="Folder containing .pdf statement files (tilde ok).",
    )
    p.add_argument(
        "--output-dir",
        default="~/data/GoogleDrive/My Drive/People/Ian Sweeney/Financial Transactions/SSACRD (5229 4890 4592 9253)/Transactions (CSV)",
        help="Folder to write .xlsx files into (tilde ok).",
    )
    p.add_argument(
        "--recursive",
        action="store_true",
        help="Recurse into subfolders for PDFs.",
    )
    p.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip conversion if the target .xlsx already exists.",
    )
    p.add_argument(
        "--converter",
        default="src/scripts/ssacrd_pdf_to_xlsx.py",
        help="Path to your converter script.",
    )
    ns = p.parse_args(argv)

    in_dir = Path(ns.input_dir).expanduser()
    out_dir = Path(ns.output_dir).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_dir.exists():
        print(f"Input directory not found: {in_dir}", file=sys.stderr)
        return 2

    pdf_iter = in_dir.rglob("*.pdf") if ns.recursive else in_dir.glob("*.pdf")
    pdfs = sorted(pdf_iter)
    if not pdfs:
        print(f"No PDFs found in {in_dir}", file=sys.stderr)
        return 1

    ok = 0
    fail = 0

    for pdf_path in pdfs:
        output_xlsx = out_dir / (pdf_path.stem + ".xlsx")

        if ns.skip_existing and output_xlsx.exists():
            print(f"↷ Skipping (exists): {output_xlsx}")
            continue

        print(f"→ Converting {pdf_path} → {output_xlsx}")
        try:
            # Call your converter with safe args (no shell quoting woes).
            subprocess.run(
                [sys.executable, ns.converter, str(pdf_path), str(output_xlsx)],
                check=True,
            )
            ok += 1
        except subprocess.CalledProcessError as e:
            print(f"✗ FAILED for {pdf_path}: {e}", file=sys.stderr)
            fail += 1

    print(f"\nDone. {ok} succeeded, {fail} failed.")
    return 0 if fail == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())
