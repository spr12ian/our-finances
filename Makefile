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

REQUIRED_VARS := \
  GOOGLE_DRIVE_OUR_FINANCES_KEY \
	GOOGLE_SERVICE_ACCOUNT_KEY_FILE \
	SQLITE_DB_LOCATION \
	SQLITE_OUR_FINANCES_DB_NAME
export $(REQUIRED_VARS)

SRC := src tests

.DEFAULT_GOAL := help

.PHONY: \
	all \
	analyze-spreadsheet \
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
	download-sheets-to-sqlite \
	format \
	format_check \
	generate-reports \
	help \
	info \
	install_package \
	install_tools \
	key-check \
	lint \
	output \
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

all: setup test_only

setup: clean install_tools update ## Set up the environment and tools
	@echo "✅ Setup complete."

install_package: ## Install a dev dependency and persist to pyproject.toml
	@test "$(PACKAGE)" || (echo "❌ Must provide PACKAGE=<name>"; exit 1)
	@echo "📦 Installing $(PACKAGE) into dev environment..."
	@hatch run dev:pip install "$(PACKAGE)"
	@echo "🗘️ Adding $(PACKAGE) to [tool.hatch.envs.dev] in pyproject.toml..."
	@sed -i '/^\[tool\.hatch\.envs\.dev\]/,/^\[/{/dependencies = \[/a\    "$(PACKAGE)",}' pyproject.toml
	@$(MAKE) update
	@echo "✅ $(PACKAGE) installed and environment updated."

install_tools:
	pipx upgrade ruff || pipx install ruff
	pipx upgrade mypy || pipx install mypy

requirements:
	@echo "🚀 Upgrading pip, setuptools, and wheel..."
	pip install --upgrade pip setuptools wheel

info:
	@echo "GOOGLE_DRIVE_OUR_FINANCES_KEY=$(GOOGLE_DRIVE_OUR_FINANCES_KEY)"
	@echo "GOOGLE_SERVICE_ACCOUNT_KEY_FILE=$(GOOGLE_SERVICE_ACCOUNT_KEY_FILE)"

clean: output ## Clean-up the directory
	@echo "🧹 Cleaning up..."
	@rm -rf .venv .mypy_cache .ruff_cache .pytest_cache dist build
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -delete
	@find . -type f -name '*.stderr' -print | tee output/deleted_stderr.txt | xargs -r rm -f
	@find . -type f -name '*.stdout' -print | tee output/deleted_stdout.txt | xargs -r rm -f
	@echo "✅ Cleaned."

key-check: check_env ## Run key-check to test connection to the spreadsheet
	@$(MAKE) run_with_log ACTION=key-check COMMAND="hatch run key-check"

analyze-spreadsheet: check_env
	@$(MAKE) run_with_log ACTION=analyze-spreadsheet COMMAND="hatch run analyze-spreadsheet"

db:
	@$(MAKE) run_with_log ACTION=db COMMAND="sqlitebrowser $(SQLITE_OUR_FINANCES_DB_NAME) &;"
	db-browser: echo "sqlitebrowser $(SQLITE_OUR_FINANCES_DB_NAME) should be running."

download-sheets-to-sqlite: check_env
	@$(MAKE) run_with_log ACTION=download-sheets-to-sqlite COMMAND="hatch run download-sheets-to-sqlite"
	@echo "sqlitebrowser ${SQLITE_OUR_FINANCES_DB_NAME} or sqlite3 ${SQLITE_OUR_FINANCES_DB_NAME}"

generate-reports: check_env
	@$(MAKE) run_with_log ACTION=generate-reports COMMAND="hatch run generate-reports"

first-normal-form: check_env
	@$(MAKE) run_with_log ACTION=first-normal-form COMMAND="hatch run first-normal-form"

vacuum-sqlite-database: check_env
	@$(MAKE) run_with_log ACTION=vacuum-sqlite-database COMMAND="hatch run vacuum-sqlite-database"

ci: lint format_check types test_only
	@echo "✅ CI checks passed."

test: lint format types test_only
	@echo "Running tests..."
	@$(MAKE) key-check
	@$(MAKE) analyze-spreadsheet
	@$(MAKE) download-sheets-to-sqlite
	@$(MAKE) vacuum-sqlite-database
	@$(MAKE) generate-reports
	@$(MAKE) first-normal-form
	@$(MAKE) execute_sqlite_queries
	@$(MAKE) generate_sqlalchemy_models
	@$(MAKE) execute_sqlalchemy_queries
	hatch run dev:test
	@echo "✅ Tests completed."

check: format_check types test_only
	@$(MAKE) lint
	@$(MAKE) test
	@echo "✅ All checks passed."

lint: output
	@log_file="output/lint.log"; \
	echo "🔍 Linting ..." | tee "$$log_file"; \
	hatch run dev:check | tee -a "$$log_file"

format: output
	@log_file="output/format.log"; \
	echo "🎨 Formatting with ruff..." | tee "$$log_file"; \
	hatch run ruff format . | tee -a "$$log_file"

format_check: output
	@log_file="output/format_check.log"; \
	echo "🎨 Checking formatting with ruff (check mode)..." | tee "$$log_file"; \
	hatch run ruff format --check --diff $(SRC) | tee -a "$$log_file"

test_all:
	@echo "🔮 Running pytest..."
	@hatch run pytest --maxfail=1 --disable-warnings -q

test_only: output
	@log_file="output/test_only.log"; \
	echo "🔮 Running isolated unit tests..." | tee "$$log_file"; \
	hatch run pytest tests --maxfail=1 --disable-warnings -q | tee -a "$$log_file"
	echo "✅ Unit tests complete." | tee -a "$$log_file"

tree: output
	@$(MAKE) run_with_log ACTION=tree COMMAND="tree -a -F -I '__pycache__|.git|.hatch|.mypy_cache|.pytest_cache|.ruff_cache|.venv'"

types: output
	@log_file="output/types.log"; \
	echo "🔎 Type checking with mypy..." | tee "$$log_file"; \
	hatch run mypy --explicit-package-bases $(SRC) | tee -a "$$log_file"

check_env:
	@missing=0; \
	for var in $(REQUIRED_VARS); do \
		if [ -z "$$\{!var\}" ]; then \
			echo "❌ Environment variable '$$var' is not set."; \
			missing=1; \
		else \
			echo "✅ $$var is set."; \
		fi; \
	done; \
	if [ "$$missing" -eq 1 ]; then \
		echo "⚠️ One or more required environment variables are missing."; \
		exit 1; \
	else \
		echo "✅ All required environment variables are set."; \
	fi

output:
	@install -d output

run_with_log: output
	@log_file="output/$(ACTION).txt"; \
	stdout_file="output/$(ACTION).stdout"; \
	stderr_file="output/$(ACTION).stderr"; \
	color_log() { printf "\033[1;34m🔧 Starting %s...\033[0m\n" "$(ACTION)"; }; \
	color_log_end() { printf "\033[1;32m✅ %s finished.\033[0m\n" "$(ACTION)"; }; \
	color_log | tee "$$log_file"; \
	{ \
	  { eval $(COMMAND); } 2> >(tee "$$stderr_file" >&2); \
	} | tee "$$stdout_file" -a "$$log_file"; \
	cat "$$stderr_file" >> "$$log_file"; \
	color_log_end | tee -a "$$log_file"


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

run:
	@$(MAKE) run_with_log ACTION=$(ACTION) COMMAND=$(COMMAND)

run_queries: check_env
	@$(MAKE) run_with_log ACTION=execute_sqlite_queries COMMAND="hatch run execute_sqlite_queries $(FILE)"

shell: ## Enter Hatch dev environment shell
	hatch shell dev

update: ## Recreate hatch with current pyproject.toml
	@echo "🔄 Recreating Hatch environment..."
	@hatch env prune
	@hatch env create dev
	@echo "✅ Hatch environment recreated."

version: ## Show current project version
	hatch version

bump-patch:
	hatch version patch && git commit -am "bump: patch version" && git tag v$$(hatch version)

bump-minor:
	hatch version minor && git commit -am "bump: minor version" && git tag v$$(hatch version)

bump-major:
	hatch version major && git commit -am "bump: major version" && git tag v$$(hatch version)
