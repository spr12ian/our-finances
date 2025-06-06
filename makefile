# ============================
# Configuration
# ============================
SHELL := /bin/bash

GOOGLE_SERVICE_ACCOUNT_KEY ?= service-account.json

VENV_DIR := .venv
PYTHON := python3
VPYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip
REQUIREMENTS := requirements.txt

TOP_LEVEL_PACKAGES := \
	google-auth \
	gspread \
	jinja2 \
	libcst \
	pandas \
	pytest \
	pyyaml \
	sqlalchemy \
	types-PyYAML

.DEFAULT_GOAL := all

.PHONY: \
	activate \
	all \
	analyze_spreadsheet \
	batch \
	ci \
	clean \
	freeze \
	google_sheets_to_sqlite \
	info \
	install_tools \
	key_check \
	pipx \
	requirements \
	setup \
	test \
	test_only \
	venv

# ============================
# Meta targets
# ============================

all: setup test_only

activate: venv
	@echo "Run this to activate the virtual environment:"
	@echo "source $(VENV_DIR)/bin/activate"

setup: requirements install_tools
	@echo "✅ Setup complete."

# ============================
# Virtual environment
# ============================

venv:
	@echo "🔧 Creating virtual environment in $(VENV_DIR) if it doesn't exist..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "✅ Created virtual environment"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi

# ============================
# Package installation
# ============================

pipx: venv
	@if ! command -v pipx > /dev/null; then \
		echo "📦 Installing pipx..."; \
		$(PYTHON) -m pip install --user pipx; \
		$(PYTHON) -m pipx ensurepath; \
		echo "Please restart your shell or run 'source ~/.profile' to update PATH."; \
		exit 1; \
	else \
		echo "✅ pipx already installed"; \
	fi

install_tools: pipx
	pipx install --force ruff
	pipx install --force black
	pipx install --force mypy

requirements: venv
	@echo "🚀 Upgrading pip, setuptools, and wheel..."
	$(PIP) install --upgrade pip setuptools wheel
ifeq ("$(wildcard $(REQUIREMENTS))","")
	@echo "📦 Installing top-level packages: $(TOP_LEVEL_PACKAGES)"
	$(PIP) install $(TOP_LEVEL_PACKAGES)
	@echo "📝 Writing top-level-only requirements.txt"
	@echo "# Top-level dev dependencies" > $(REQUIREMENTS)
	@for pkg in $(TOP_LEVEL_PACKAGES); do echo $$pkg >> $(REQUIREMENTS); done
else
	@echo "📜 Installing from existing $(REQUIREMENTS)..."
	$(PIP) install -r $(REQUIREMENTS)
endif

freeze:
	@echo "📌 Rewriting $(REQUIREMENTS) with top-level-only packages..."
	@echo "# Top-level dev dependencies" > $(REQUIREMENTS)
	@for pkg in $(TOP_LEVEL_PACKAGES); do echo $$pkg >> $(REQUIREMENTS); done
	@echo "✅ Updated."

# ============================
# Info + Utility
# ============================

info:
	@echo "$GOOGLE_DRIVE_OUR_FINANCES_KEY=$(GOOGLE_SERVICE_ACCOUNT_KEY_FILE)"
	@echo "GOOGLE_SERVICE_ACCOUNT_KEY_FILE:"
	@if echo '$(GOOGLE_SERVICE_ACCOUNT_KEY_FILE)' | grep -q '^{'; then \
		echo '$(GOOGLE_SERVICE_ACCOUNT_KEY_FILE)' | jq .; \
	else \
		cat "$(GOOGLE_SERVICE_ACCOUNT_KEY_FILE)" | jq .; \
	fi

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
	@rm -rf $(REQUIREMENTS)
	@echo "✅ Cleaned all caches and virtual environment."

# ============================
# Scripts
# ============================

analyze_spreadsheet: check_env requirements
	@$(VPYTHON) -m scripts.analyze_spreadsheet
	@echo "✅ Spreadsheet analysed."

google_sheets_to_sqlite: check_env requirements
	@$(VPYTHON) -m scripts.google_sheets_to_sqlite

key_check: check_env requirements
	@$(VPYTHON) -m scripts.key_check

# ============================
# Testing & Batching
# ============================

ci: lint format-check types test-only
	@echo "✅ CI checks passed."

test: lint format types test-only
	@echo "Running tests..."
	@$(MAKE) key_check
	@$(MAKE) analyze_spreadsheet
	@$(MAKE) google_sheets_to_sqlite
	@$(MAKE) vacuum_sqlite_database
	@echo "✅ Tests completed."

# ============================
# Linting & Formatting
# ============================

lint: install_tools
	@echo "🔍 Linting with ruff..."
	@$(VENV_DIR)/bin/ruff check src scripts tests

format: install_tools
	@echo "🎨 Formatting with black..."
	@$(VENV_DIR)/bin/black src scripts tests

format-check: install_tools
	@echo "🎨 Checking formatting with black (check mode)..."
	@$(VENV_DIR)/bin/black --check --diff src scripts tests

test-all: requirements
	@echo "🧪 Running pytest..."
	@$(VENV_DIR)/bin/pytest --maxfail=1 --disable-warnings -q

test-only: requirements
	@echo "🧪 Running isolated unit tests..."
	@$(VPYTHON) -m pytest tests --maxfail=1 --disable-warnings -q
	@echo "✅ Unit tests complete."

types: 
	@echo "🔎 Type checking with mypy..."
	@$(VPYTHON) -m mypy src scripts tests


check_env:
	@vars="GOOGLE_DRIVE_OUR_FINANCES_KEY GOOGLE_SERVICE_ACCOUNT_KEY_FILE"; \
	for var in $$vars; do \
		if [ -z "$${!var}" ]; then \
			echo "❌ Environment variable $$var is not set."; \
			exit 1; \
		else \
			echo "✅ $$var is set."; \
		fi; \
	done

