import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pdfplumber


@dataclass()
class Transaction:
    date: str
    description: str
    credit: str = ""
    debit: str = ""

    def __str__(self) -> str:
        if self.credit:
            amount = float(self.credit.replace(",", ""))
            return f"{self.date},{self.description},{amount:.2f},"
        else:
            amount = float(self.debit.replace(",", ""))
            return f"{self.date},{self.description},,{amount:.2f}"


def main() -> None:
    pdf_path = "2025-02.pdf"  # your PDF statement
    output_csv = "transactions_2025_02.csv"

    # --- helpers ---------------------------------------------------------------

    MONTHS = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }

    TXN_RE = re.compile(
        r"""
            ^\s*
            (?P<day>\d{1,2})(?:st|nd|rd|th)?   # day
            \s+
            (?P<month>[A-Za-z]{3,9})           # month
            (?:\s+(?P<year>\d{4}))?            # optional year
            \s+
            (?P<desc>.*?)                      # description (lazy)
            (?:\s+(?P<cr>CR))?                 # optional trailing CR token
            \s+
            (?P<amount>                        # amount (with () / £ / sign / thousands)
                \(?£?\s*[-+]?
                (?:\d{1,3}(?:,\d{3})+|\d+)
                (?:\.\d{2})?
                \)?
            )
            \s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    FILENAME_YM = re.compile(r"(?P<year>\d{4})-(?P<month>\d{2})", re.IGNORECASE)

    def parse_statement_year(pdf_file: str) -> int:
        m = FILENAME_YM.search(Path(pdf_file).name)
        if m:
            return int(m.group("year"))
        # fallback to current year if not encoded in filename
        return datetime.now().year

    def parse_date(day: str, month: str, year: str | None, default_year: int) -> str:
        m = month.lower()
        if m not in MONTHS:
            raise ValueError(f"Unrecognized month: {month}")
        y = int(year) if year else default_year
        d = datetime(y, MONTHS[m], int(day))
        return d.strftime("%d/%m/%Y")

    # --- extraction -------------------------------------------------------

    lines: list[str] = []
    statement_year = parse_statement_year(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            for raw_line in text.splitlines():
                line = raw_line.rstrip()
                # print(f"line: {line}")

                if line.startswith("Total Cashback awarded previous month CR"):
                    # Handle special case for total line
                    m = re.search(r"[-+]?(?:\d+\.\d+|\.\d+)", line)
                    credit = m.group() if m else ""

                    transaction = Transaction("17/01/2025", "CASHBACK", credit)
                    print(transaction)

                    continue

                m = TXN_RE.match(line)
                if m:
                    # print(f"m: {m}")

                    gd = m.groupdict()
                    date_iso = parse_date(
                        gd["day"], gd["month"], gd.get("year"), statement_year
                    )
                    if gd.get("cr") == "CR":
                        credit = ""
                        debit = gd["amount"]
                    else:
                        credit = gd["amount"]
                        debit = ""

                    transaction = Transaction(
                        date_iso, gd["desc"].strip(), credit, debit
                    )

                    lines.append(str(transaction))

    output = ""
    for line in lines:
        output += line + "\n"

    with open(output_csv, "a") as file:
        file.write(output)

    print(f"Extracted {len(lines)} transactions → {output_csv}")


if __name__ == "__main__":
    main()
