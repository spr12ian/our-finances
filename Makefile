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
	check_env \
	ci \
	clean \
	format_check \
	help \
	install_hatch_plugin \
	install_pip_package \
	output \
	run_with_log \
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
	@$(MAKE) check_env
	@$(MAKE) update
	@$(MAKE) version
	@$(MAKE) format
	@$(MAKE) fownes-street
#	@$(MAKE) lint
	@$(MAKE) key-check
	@$(MAKE) analyze-spreadsheet
	@$(MAKE) download-sheets-to-sqlite
	@$(MAKE) generate-reports
	@$(MAKE) pre_commit_check
# what follows is really future development
	@$(MAKE) vacuum-sqlite-database
	@$(MAKE) first-normal-form
	@$(MAKE) execute_sqlite_queries
	@$(MAKE) generate_sqlalchemy_models
	@$(MAKE) execute_sqlalchemy_queries
	@echo "✅ All steps completed."

check_env: ## Check required env variables are set
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

format_check: output ## Check but don't make changes???
	@log_file="output/format_check.log"; \
	echo "🎨 Checking formatting with ruff (check mode)..." | tee "$$log_file"; \
	hatch run ruff format --check --diff $(SRC) | tee -a "$$log_file"

hatch-%:
	@$(MAKE) run_with_log ACTION=$* COMMAND="hatch run $*"

help: ## Lists available targets
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	sort | \
	awk 'BEGIN {FS=":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@# --- add dynamically-generated targets ---
	@for t in $(scripts); do \
		printf "\033[36m%-25s\033[0m %s\n" "$$t" "hatch run $$t"; \
	done
	@for t in $(tools); do \
		printf "\033[36m%-25s\033[0m %s\n" "$$t" "hatch run dev:$$t"; \
	done
	@printf "\033[36m%-25s\033[0m %s\n" "all-tools"  "Run all tool tasks"

install_hatch_plugin: ## Install a Hatch plugin (via pipx inject)
	@test "$(PLUGIN)" || (echo "❌ Must provide PLUGIN=<name>"; exit 1)
	@echo "🔌 Installing Hatch plugin $(PLUGIN)..."
	pipx inject hatch "$(PLUGIN)"
	@echo "✅ Plugin $(PLUGIN) installed into Hatch environment."

install_pip_package: ## Install a dev pip dependency and persist to pyproject.toml
	@test "$(PACKAGE)" || (echo "❌ Must provide PACKAGE=<name>"; exit 1)
	@echo "📦 Installing pip $(PACKAGE) into dev environment..."
	@hatch run dev:pip install "$(PACKAGE)"
	@echo "🗘️ Adding $(PACKAGE) to [tool.hatch.envs.dev] in pyproject.toml..."
	@sed -i '/^\[tool\.hatch\.envs\.dev\]/,/^\[/{/dependencies = \[/a\    "$(PACKAGE)",}' pyproject.toml
	@$(MAKE) update
	@echo "✅ $(PACKAGE) installed and environment updated."

output:
	@install -d output

run_with_log: output
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

shell: ## Enter Hatch dev environment shell
	hatch shell dev

sqlite3: check_env ## SQLite command line
	@sqlite3 ${SQLITE_OUR_FINANCES_DB_NAME}

sqlitebrowser: check_env ## SQLite GUI
	@sqlitebrowser ${SQLITE_OUR_FINANCES_DB_NAME}

tree: output ## Current project tree
	@$(MAKE) run_with_log ACTION=tree COMMAND="tree -a -F -I $(TREE_EXCLUDES)"

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
$1: check_env ## hatch run $(1)
	@$$(MAKE) run_with_log ACTION="$1" COMMAND="hatch run $1"
endef

# tools
define run-tool
$1: ## hatch run dev:"$(1)"
	@$$(MAKE) run_with_log ACTION="$1" COMMAND="hatch run dev:$1"
endef

scripts := \
    fownes-street \
    key-check \
    analyze-spreadsheet \
    download-sheets-to-sqlite \
    generate-reports \
	first-normal-form \
	vacuum-sqlite-database

tools := \
    format \
    lint \
    run_tests \
    pre_commit_check \
	run_queries

$(foreach target,$(scripts),$(eval $(call run-script,$(target))))
$(foreach target,$(tools),$(eval $(call run-tool,$(target))))
