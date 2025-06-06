# Customize these
GOOGLE_SERVICE_ACCOUNT_KEY ?= service-account.json

# Configuration
VENV_DIR := .venv
PYTHON := python3
REQUIREMENTS := requirements.txt
TOP_LEVEL_PACKAGES := google-auth gspread libcst mypy pandas pyyaml sqlalchemy types-PyYAML

.PHONY: activate all analyze_spreadsheet clean freeze google_sheets_to_sqlite info key_check setup test

all: setup test

activate:
	@echo "Run this to activate the virtual environment:"
	@echo "source $(VENV_DIR)/bin/activate"

analyze_spreadsheet:
	@$(VENV_DIR)/bin/python -m our_finances analyze_spreadsheet

clean:
	@echo "🧹 Removing virtual environment..."
	@rm -rf $(VENV_DIR)
	@echo "🧹 Removing all __pycache__ directories..."
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@echo "🧹 Removing .mypy_cache directory..."
	@rm -rf .mypy_cache
	@echo "🧹 Removing log files..."
	@rm -rf *.log
	@echo "🧹 Removing requirements.txt ..."
	@rm -rf requirements.txt
	@echo "✅ Cleaned all caches and virtual environment."

freeze:
	@echo "📌 Rewriting $(REQUIREMENTS) with top-level-only packages..."
	@echo "# Top-level dev dependencies" > $(REQUIREMENTS)
	@for pkg in $(TOP_LEVEL_PACKAGES); do echo $$pkg >> $(REQUIREMENTS); done
	@echo "✅ Updated."

google_sheets_to_sqlite:
	@$(VENV_DIR)/bin/python -m our_finances google_sheets_to_sqlite

# Show current configuration
info:
	@echo "GOOGLE_SERVICE_ACCOUNT_KEY:"
	@if echo '$(GOOGLE_SERVICE_ACCOUNT_KEY)' | grep -q '^{'; then \
		echo '$(GOOGLE_SERVICE_ACCOUNT_KEY)' | jq .; \
	else \
		cat "$(GOOGLE_SERVICE_ACCOUNT_KEY)" | jq .; \
	fi

key_check:
	@$(VENV_DIR)/bin/python -m our_finances key_check

setup:
	@echo "🔧 Creating virtual environment in $(VENV_DIR) if it doesn't exist..."
	@test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	@echo "🚀 Upgrading pip, setuptools, and wheel..."
	$(VENV_DIR)/bin/python -m pip install --upgrade pip setuptools wheel
ifeq ("$(wildcard $(REQUIREMENTS))","")
	@echo "📦 Installing top-level packages: $(TOP_LEVEL_PACKAGES)"
	$(VENV_DIR)/bin/python -m pip install $(TOP_LEVEL_PACKAGES)
	@echo "📝 Writing top-level-only requirements.txt"
	@echo "# Top-level dev dependencies" > $(REQUIREMENTS)
	@for pkg in $(TOP_LEVEL_PACKAGES); do echo $$pkg >> $(REQUIREMENTS); done
else
	@echo "📜 Installing from existing $(REQUIREMENTS)..."
	$(VENV_DIR)/bin/python -m pip install -r $(REQUIREMENTS)
endif
	@echo "✅ Setup complete."

test:
	@echo "Running tests..."
	@$(VENV_DIR)/bin/python -m our_finances key_check
	@$(VENV_DIR)/bin/python -m our_finances analyze_spreadsheet
	@$(VENV_DIR)/bin/python -m our_finances google_sheets_to_sqlite
	@$(VENV_DIR)/bin/python -m our_finances vacuum_sqlite_database
#	@$(VENV_DIR)/bin/python -m pytest --maxfail=1 --disable-warnings -q
	@echo "✅ Tests completed."
