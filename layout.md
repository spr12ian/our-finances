our-finances/
├── .vscode/                      # VS Code settings and config
│   └── settings.json             # Python interpreter and linting setup
├── config/                       # Metadata and rule definitions
│   ├── accounts.yaml             # Mapping account codes to owners
│   └── categories.yaml           # Categorisation rules
├── data/                         # Data inputs and outputs
│   ├── raw/                      # Optional cached Google Sheets exports
│   └── processed/                # Cleaned data or local SQLite database
├── notebooks/                    # Jupyter notebooks for ad hoc exploration
│   └── analysis.ipynb            # Data insights, charts, etc.
├── reports/                      # Generated tax and finance reports
│   └── README.md
├── script/                       # CLI-level scripts for operations
│   ├── key_check.py              # Checks we have authority to connect to the spreadsheet
│   ├── analyze_spreadsheet.py    # Get info about fields on spreadsheet
│   ├── download_sheets_to_sqlite.py  # Google Sheets to local database from analyzed data
│   ├── generate_reports.py       # Build PDFs for tax, spending
│   └── sync_counterparties.py    # Reconcile inter-account transactions
├── sheets/                       # Apps Script code for menu and automation
│   ├── menu.gs                   # Custom menu entries
│   └── categorise.gs             # Optional rule-based categorisation
├── src/                          # Python source logic (importable as package)
│   └── finances/
│       ├── __init__.py
│       ├── loader.py             # Data fetching/parsing logic
│       ├── categories.py         # Category assignment functions
│       ├── balance_check.py      # Sanity and reconciliation checks
│       └── reports.py            # Generate report content/data
├── tests/                          # Pytest tests
│   └── test_categories.py
├── .gitignore                      # Ignore venv, .env, data, etc.
├── requirements.txt                # pip dependencies
├── pyproject.toml                  # Formatting, linting, tool config
└── README.md                       # Project overview and usage



# .vscode/settings.json
{
  "python.pythonPath": "venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.flake8Enabled": true,
  "python.testing.pytestEnabled": true
}


# src/finances/categories.py
def classify_transaction(note, rules):
    for category, patterns in rules.items():
        if any(p.lower() in note.lower() for p in patterns):
            return category
    return "Uncategorised"




## 🧩 Layout Diagram
You can generate visual diagrams using VS Code extensions like:
- "Project Tree Generator" (ASCII-style tree views)
- "Markdown Preview Mermaid Support" (for Mermaid diagrams)
- "Draw.io Integration" (GUI diagrams)

Example Mermaid diagram (put in README.md or a `.md` file):


