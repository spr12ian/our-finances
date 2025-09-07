ifeq ("$(wildcard $(HOME)/.env)","")
$(warning ⚠️  No ~/.env file found. Environment variables may not be set.)
endif

# ============================
# Configuration
# ============================
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

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

TREE_EXCLUDES := '__pycache__|.git|.hatch|.mypy_cache|.pytest_cache|.ruff_cache|.venv'

.DEFAULT_GOAL := help

.PHONY: \
	all \
	check-env \
	ci \
	clean \
	format-check \
	hatch-build \
	hatch-clean \
	hatch-update \
	help \
	install-hatch-plugin \
	install-pip-package \
	output \
	_run-with-log \
	shell \
	sqlite3 \
	sqlitebrowser \
	tree \
	types \
	update \
	version \
	$(scripts) \
	$(tools)

all: ## Run all steps
	@echo "Running all steps..."
	@$(MAKE) clean
	@$(MAKE) check-env
	@$(MAKE) ssacrd-pdfs-to-xlsx
	@$(MAKE) update
	@$(MAKE) version
	@$(MAKE) format
	@$(MAKE) fownes-street
#	@$(MAKE) lint
	@$(MAKE) key-check
	@$(MAKE) analyze-spreadsheet
	@$(MAKE) download-sheets-to-sqlite
	@$(MAKE) generate-reports
	@$(MAKE) pre-commit-check
# what follows is really future development
	@$(MAKE) vacuum-sqlite-database
	@$(MAKE) first-normal-form
	@$(MAKE) execute-sqlite-queries
	@$(MAKE) generate-sqlalchemy-models
	@$(MAKE) execute-sqlalchemy-queries
	@echo "✅ All steps completed."

check-env: ## Check required env variables are set
	@missing=0; \
	for var in $(REQUIRED_VARS); do \
		if [ -z "$$\{!var\}" ]; then \
			echo "❌ Environment variable '$$var' is not set."; \
			missing=1; \
		else \
			echo "✅ $$var is set to $${!var}."; \
		fi; \
	done; \
	if [ "$$missing" -eq 1 ]; then \
		echo "⚠️ One or more required environment variables are missing."; \
		exit 1; \
	else \
		echo "✅ All required environment variables are set."; \
	fi

ci: lint format_check types ## Check CI still works
	@echo "✅ CI checks passed."

clean: output ## Clean-up the directory
	@echo "🧹 Cleaning up..."
	@timestamp="$$(date '+%F_%H-%M')"; \
	stdout_file="output/$${timestamp}_deleted_stdout.txt"; \
	stderr_file="output/$${timestamp}_deleted_stderr.txt"; \
	mkdir -p output; \
	rm -rf .venv .mypy_cache .ruff_cache .pytest_cache dist build; \
	find . -type d -name '__pycache__' -exec rm -rf {} +; \
	find . -type f -name '*.py[co]' -delete; \
	find . -type f -name '*.stderr' -print | tee "$$stderr_file" | xargs -r rm -f; \
	find . -type f -name '*.stdout' -print | tee "$$stdout_file" | xargs -r rm -f; \
	echo "✅ Cleaned."

format-check: output ## Check but don't make changes???
	@log_file="output/format_check.log"; \
	echo "🎨 Checking formatting with ruff (check mode)..." | tee "$$log_file"; \
	hatch run ruff format --check --diff $(SRC) | tee -a "$$log_file"

hatch-build: ## Build the project (hatch build)
	@echo "🏗️ Building the project with hatch..."
	@hatch build
	@echo "✅ Project built."

hatch-clean: ## Clean hatch build artifacts
	@echo "🧹 Cleaning hatch build artifacts..."
	@hatch env prune
	@echo "✅ Hatch build artifacts cleaned."

hatch-update: ## Update hatch environment (hatch env update)
	@echo "🔄 Updating Hatch environment..."
	@hatch env remove default || true
	@hatch run python --version
	@echo "✅ Hatch environment updated."

hatch-run-%:
	@$(MAKE) _run-with-log ACTION=$* COMMAND="hatch run $*"

help: ## Lists available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort | \
	awk 'BEGIN {FS=":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@# --- add dynamically-generated targets ---
	@for t in $(scripts); do \
		printf "\033[36m%-25s\033[0m %s\n" "$$t" "hatch run $$t"; \
	done
	@for t in $(tools); do \
		printf "\033[36m%-25s\033[0m %s\n" "$$t" "hatch run $$t"; \
	done
	@printf "\033[36m%-25s\033[0m %s\n" "all-tools"  "Run all tool tasks"

install-hatch-plugin: ## Install a Hatch plugin (via pipx inject)
	@test "$(PLUGIN)" || (echo "❌ Must provide PLUGIN=<name>"; exit 1)
	@echo "🔌 Installing Hatch plugin $(PLUGIN)..."
	pipx inject hatch "$(PLUGIN)"
	@echo "✅ Plugin $(PLUGIN) installed into Hatch environment."

install-pip-package: ## Install a pip dependency and persist to pyproject.toml
	@test "$(PACKAGE)" || (echo "❌ Must provide PACKAGE=<name>"; exit 1)
	@echo "📦 Installing pip $(PACKAGE) into default environment..."
	@hatch run pip install "$(PACKAGE)"
	@echo "🗘️ Adding $(PACKAGE) to [project.optional-dependencies].all in pyproject.toml..."
	@sed -i '/^\[project\.optional-dependencies\]/,/^\[/{/^\s*all\s*=\s*\[/a\  "$(PACKAGE)",}' pyproject.toml
	@$(MAKE) update
	@echo "✅ $(PACKAGE) installed and environment updated."

output:
	@install -d output

_run-with-log: output
	@timestamp="$$(date '+%F_%H:%M')"; \
	log_file="output/$${timestamp}_$(ACTION).txt"; \
	stdout_file="output/$${timestamp}_$(ACTION).stdout"; \
	stderr_file="output/$${timestamp}_$(ACTION).stderr"; \
	echo "$$COMMAND"; \
	color_log() { printf "\033[1;34m🔧 Starting %s...\033[0m\n" "$(ACTION)"; }; \
	color_log_end() { printf "\033[1;32m✅ %s finished.\033[0m\n" "$(ACTION)"; }; \
	color_log | tee "$$log_file"; \
	{ \
	  { eval "$(COMMAND)"; } 2> >(tee "$$stderr_file" >&2); \
	} | tee "$$stdout_file" -a "$$log_file"; \
	cat "$$stderr_file" >> "$$log_file"; \
	color_log_end | tee -a "$$log_file"; \
	for f in "$$log_file" "$$stdout_file" "$$stderr_file"; do \
	  [ -s "$$f" ] || rm -f "$$f"; \
	done

shell: ## Enter Hatch default environment shell
	hatch shell

sqlite3: check-env ## SQLite command line
	@sqlite3 ${SQLITE_OUR_FINANCES_DB_NAME}

sqlitebrowser: check-env ## SQLite GUI
	@sqlitebrowser ${SQLITE_OUR_FINANCES_DB_NAME}

tree: output ## Current project tree
	@$(MAKE) _run-with-log ACTION=tree COMMAND="tree -a -F -I $(TREE_EXCLUDES)"

types: output
	@log_file="output/types.log"; \
	echo "🔎 Type checking with mypy..." | tee "$$log_file"; \
	hatch run mypy --explicit-package-bases $(SRC) | tee -a "$$log_file"

update: ## Recreate hatch with current pyproject.toml
	@echo "🔄 Recreating Hatch environment..."
	@hatch env prune
	@hatch env create dev
	@echo "✅ Hatch environment recreated."

version: ## Show current project version
	hatch version

# scripts
define run-script
$1: check-env ## hatch run $(1)
	@$$(MAKE) _run-with-log ACTION="$1" COMMAND="hatch run $1"
endef

# tools
define run-tool
$1: ## hatch run"$(1)"
	@$$(MAKE) _run-with-log ACTION="$1" COMMAND="hatch run $1"
endef

scripts := \
    ssacrd-pdfs-to-xlsx \
    fownes-street \
    key-check \
    analyze-spreadsheet \
    download-sheets-to-sqlite \
    generate-reports \
	first-normal-form \
	vacuum-sqlite-database \
	execute-sqlite-queries \
	execute-sqlalchemy-queries \
	generate-sqlalchemy-models


tools := \
    format \
    lint \
    run-tests \
    pre-commit-check \
	run-queries

$(foreach target,$(scripts),$(eval $(call run-script,$(target))))
$(foreach target,$(tools),$(eval $(call run-tool,$(target))))
