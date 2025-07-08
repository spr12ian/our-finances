ifeq ("$(wildcard $(HOME)/.env)","")
$(warning ⚠️  No ~/.env file found. Environment variables may not be set.)
endif

# ============================
# Configuration
# ============================
SHELL := /bin/bash

ENV_FILE := $(HOME)/.env
include_env = . $(ENV_FILE) >/dev/null 2>&1 &&

GOOGLE_SERVICE_ACCOUNT_KEY_FILE ?= service-account.json
SQLITE_DB_LOCATION ?= data/processed
SQLITE_OUR_FINANCES_DB_NAME ?= our_finances

VENV_DIR := .venv
PYTHON := python3
VPYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

REQUIRED_VARS := \
  GOOGLE_DRIVE_OUR_FINANCES_KEY \
	GOOGLE_SERVICE_ACCOUNT_KEY_FILE \
	SQLITE_DB_LOCATION \
	SQLITE_OUR_FINANCES_DB_NAME
export $(REQUIRED_VARS)

REQUIREMENTS := requirements.txt

# Project source locations
SRC := src scripts tests

TOP_LEVEL_PACKAGES := \
	google-auth \
	gspread \
	jinja2 \
	libcst \
	pandas \
	pytest \
	pyyaml \
	sqlalchemy \
	sqlparse \
	types-PyYAML

.DEFAULT_GOAL := help

.PHONY: \
	all \
	analyze_spreadsheet \
	batch \
	bump-major \
	bump-minor \
	bump-patch \
	check \
	check_env \
	ci \
	clean \
	db \
	freeze \
	download_sheets_to_sqlite \
	format \
	format_check \
	generate_reports \
	help \
	info \
	install_package \
	install_tools \
	key_check \
	lint \
	logs \
	pipx \
	requirements \
	run_queries \
	run_with_log \
	setup \
	shell \
	test \
	test_all \
	test_only \
	types \
	update \
	version

# ============================
# Meta targets
# ============================

all: setup test_only



setup: clean requirements install_tools ## Set up the environment and tools
	@echo "✅ Setup complete."



# ============================
# Package installation
# ============================

install_package: ## Install a dev dependency and persist to pyproject.toml
	@test "$(PACKAGE)" || (echo "❌ Must provide PACKAGE=<name>"; exit 1)
	@echo "📦 Installing $(PACKAGE) into dev environment..."
	@hatch run dev:pip install "$(PACKAGE)"
	@echo "📝 Adding $(PACKAGE) to [tool.hatch.envs.dev] in pyproject.toml..."
	@sed -i '/^\[tool\.hatch\.envs\.dev\]/,/^\[/{/dependencies = \[/a\    "$(PACKAGE)",}' pyproject.toml
	@echo "🔁 Recreating environment..."
	@hatch env prune && hatch env create dev
	@echo "✅ $(PACKAGE) installed and environment updated."


install_tools:
	pipx ensurepath --force
	pipx upgrade ruff || pipx install ruff
	pipx upgrade mypy || pipx install mypy

requirements:
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
	@echo "GOOGLE_DRIVE_OUR_FINANCES_KEY=$(GOOGLE_DRIVE_OUR_FINANCES_KEY)"
	@echo "GOOGLE_SERVICE_ACCOUNT_KEY_FILE=$(GOOGLE_SERVICE_ACCOUNT_KEY_FILE)"


# 🧽 Clean caches and build artifacts
clean: logs ## Cleanup the directory
	@echo "🧹 Removing virtual environment..."
	@rm -rf $(VENV_DIR)
	@echo "🧹 Removing all __pycache__ directories..."
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@echo "🧹 Removing .mypy_cache directory..."
	@rm -rf .mypy_cache .ruff_cache .pytest_cache dist build
	@echo "🧹 Removing log files..."
	@find . -type f -name '*.log' -print | tee logs/deleted_logs.txt | xargs -r rm -f
	@echo "🧹 Removing requirements.txt ..."
	@rm -rf $(REQUIREMENTS)
	@find . -type f -name '*.py[co]' -delete
	@echo "✅ Cleaned all caches and virtual environment."


# ============================
# scripts
# ============================

key_check: check_env ## Run key_check to test connection to the spreadsheet
	@$(MAKE) run_with_log ACTION=key_check COMMAND="hatch run key-check"

analyze_spreadsheet: check_env ## Analyze the spreadsheet prior to downloading it
	@$(MAKE) run_with_log ACTION=analyze_spreadsheet COMMAND="$(VPYTHON) -m scripts.analyze_spreadsheet"

db:
	@$(MAKE) run_with_log ACTION=db COMMAND="sqlitebrowser $(SQLITE_OUR_FINANCES_DB_NAME) &;" \
	echo "sqlitebrowser $(SQLITE_OUR_FINANCES_DB_NAME) should be running in the background"

download_sheets_to_sqlite: check_env ## Download the spreadsheet into an SQLite database
	@$(MAKE) run_with_log ACTION=download_sheets_to_sqlite COMMAND="$(VPYTHON) -m scripts.download_sheets_to_sqlite"
	@echo "sqlitebrowser ${SQLITE_OUR_FINANCES_DB_NAME} or sqlite3 ${SQLITE_OUR_FINANCES_DB_NAME}"

generate_reports: check_env ## Create reports from the database spreadsheet data
	@$(MAKE) run_with_log ACTION=generate_reports COMMAND="$(VPYTHON) -m scripts.generate_reports"

first_normal_form: check_env ## First normal form
	@$(MAKE) run_with_log ACTION=first_normal_form COMMAND="$(VPYTHON) -m scripts.first_normal_form"

vacuum_sqlite_database: check_env ## Squeeze the database
	@$(MAKE) run_with_log ACTION=vacuum_sqlite_database COMMAND="$(VPYTHON) -m scripts.vacuum_sqlite_database"

# ============================
# Testing & Batching
# ============================

ci: lint format_check types test_only
	@echo "✅ CI checks passed."

# 🧪 Run tests
test: lint format types test_only ## Run tests using pytest
	@echo "Running tests..."
	@$(MAKE) key_check
	@$(MAKE) analyze_spreadsheet
	@$(MAKE) download_sheets_to_sqlite
	@$(MAKE) vacuum_sqlite_database
	@$(MAKE) generate_reports
	@$(MAKE) first_normal_form
	@$(MAKE) execute_sqlite_queries
	@$(MAKE) generate_sqlalchemy_models
	@$(MAKE) execute_sqlalchemy_queries
	hatch run dev:test
	@echo "✅ Tests completed."

# ============================
# Linting & Formatting
# ============================

# ✅ Check all (lint + test)
check: format_check types test_only ## Run all checks (lint + test)
	@$(MAKE) lint
	@$(MAKE) test
	@echo "✅ All checks passed."

lint: logs ## Run linters (ruff, mypy)
	@log_file="logs/lint.log"; \
	echo "🔍 Linting ..." | tee "$$log_file"; \
	hatch run dev:check | tee -a "$$log_file"

# 🎨 Auto-format code with Ruff
format: logs ## Format code with Ruff
	@log_file="logs/format.log"; \
	echo "🎨 Formatting with ruff..." | tee "$$log_file"; \
	hatch run ruff format . | tee -a "$$log_file"

format_check: logs ## Check formatting with Ruff (no changes made)
	@log_file="logs/format_check.log"; \
	echo "🎨 Checking formatting with ruff (check mode)..." | tee "$$log_file"; \
	$(include_env) ruff format --check --diff $(SRC) | tee -a "$$log_file"

test_all:
	@echo "🧪 Running pytest..."
	@$(VPYTHON) -m pytest --maxfail=1 --disable-warnings -q

test_only: logs ## Run only the test suite
	@log_file="logs/test_only.log"; \
	echo "🧪 Running isolated unit tests..." | tee "$$log_file"; \
	$(VPYTHON) -m pytest tests --maxfail=1 --disable-warnings -q | tee -a "$$log_file"
	echo "✅ Unit tests complete." | tee -a "$$log_file"

tree: logs ## list contents of directories in a tree-like format
	@$(MAKE) run_with_log ACTION=tree COMMAND="tree -a -F -I '__pycache__' -I '.git' -I '.hatch' -I '.mypy_cache' -I '.pytest_cache' -I '.ruff_cache' -I '.venv'"

types: logs ## Type check source code using Mypy
	@log_file="logs/types.log"; \
	echo "🔎 Type checking with mypy..." | tee "$$log_file"; \
	mypy --explicit-package-bases $(SRC) | tee -a "$$log_file"

check_env: ## Check that required environment variables are set
	@missing=0; \
	for var in $(REQUIRED_VARS); do \
		if [ -z "$${!var}" ]; then \
			echo "❌ Environment variable '$$var' is not set."; \
			missing=1; \
		else \
			echo "✅ $$var is set."; \
		fi; \
	done; \
	if [ "$$missing" -eq 1 ]; then \
		echo "⚠️  One or more required environment variables are missing."; \
		exit 1; \
	else \
		echo "✅ All required environment variables are set."; \
	fi


logs:
	@install -d logs

run_with_log: logs
	@log_file="logs/$(ACTION).log"; \
	echo "🔧 Starting $(ACTION)..." | tee "$$log_file"; \
	eval $(COMMAND) 2>&1 | tee -a "$$log_file"; \
	echo "✅ $(ACTION) finished." | tee -a "$$log_file"

# 🎯 Show help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run:
	@$(MAKE) run_with_log ACTION=$(ACTION) COMMAND=$(COMMAND)

run_queries: check_env
	@$(MAKE) run_with_log ACTION=execute_sqlite_queries COMMAND="$(VPYTHON) -m scripts.execute_sqlite_queries $(FILE)"

.DEFAULT_GOAL := help





# 🐚 Enter dev shell
shell: ## Enter Hatch dev environment shell
	hatch shell dev






update: ## Recreate hatch with current pyproject.toml
	@echo "🔄 Recreating Hatch environment..."
	@hatch env prune
	@hatch env create dev
	@echo "✅ Hatch environment recreated."



# 🆚 Show current version (from Git tags if using VCS versioning)
version: ## Show current project version
	hatch version

# 🔖 Version bumps (requires Git tagging workflow)
bump-patch: ## Bump patch version (x.y.Z)
	hatch version minor && git commit -am "bump: patch version" && git tag v$$(hatch version)
bump-minor: ## Bump minor version (x.Y.z)
	hatch version minor && git commit -am "bump: minor version" && git tag v$$(hatch version)
bump-major: ## Bump major version (X.y.z)
	hatch version major && git commit -am "bump: major version" && git tag v$$(hatch version)


