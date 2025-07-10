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

.DEFAULT_GOAL := help

.PHONY: \
	all \
	bump-major \
	bump-minor \
	bump-patch \
	check_env \
	ci \
	clean \
	format_check \
	help \
	info \
	install_package \
	output \
	pipx \
	run_queries \
	run_with_log \
	shell \
	test_only \
	types \
	update \
	version \
	$(scripts) \
	$(tools)


all: clean check_env update pre_commit_check ## clean check_env update pre_commit_check

hatch-%:
	@$(MAKE) run_with_log ACTION=$* COMMAND="hatch run $*"

install_package: ## Install a dev dependency and persist to pyproject.toml
	@test "$(PACKAGE)" || (echo "❌ Must provide PACKAGE=<name>"; exit 1)
	@echo "📦 Installing $(PACKAGE) into dev environment..."
	@hatch run dev:pip install "$(PACKAGE)"
	@echo "🗘️ Adding $(PACKAGE) to [tool.hatch.envs.dev] in pyproject.toml..."
	@sed -i '/^\[tool\.hatch\.envs\.dev\]/,/^\[/{/dependencies = \[/a\    "$(PACKAGE)",}' pyproject.toml
	@$(MAKE) update
	@echo "✅ $(PACKAGE) installed and environment updated."

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



ci: lint format_check types test_only
	@echo "✅ CI checks passed."



sqlitebrowser: check_env ## SQLite GUI
	@sqlitebrowser ${SQLITE_OUR_FINANCES_DB_NAME}

sqlite3: check_env ## SQLite command line
	@sqlite3 ${SQLITE_OUR_FINANCES_DB_NAME}

first-normal-form: check_env
	@$(MAKE) run_with_log ACTION=first-normal-form COMMAND="hatch run first-normal-form"

vacuum-sqlite-database: check_env
	@$(MAKE) run_with_log ACTION=vacuum-sqlite-database COMMAND="hatch run vacuum-sqlite-database"

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

format_check: output
	@log_file="output/format_check.log"; \
	echo "🎨 Checking formatting with ruff (check mode)..." | tee "$$log_file"; \
	hatch run ruff format --check --diff $(SRC) | tee -a "$$log_file"

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
	color_log_end | tee -a "$$log_file"


help:
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

# scripts
define run-script
$1: check_env ## hatch run $(1)
	$$(eval ACTION := $1)
	$$(eval COMMAND := hatch run "$(1)")
	@$$(MAKE) run_with_log ACTION="$$ACTION" COMMAND="$$COMMAND"
endef

# tools
define run-tool
$1: ## hatch run dev:"$(1)"
	$$(eval ACTION := $1)
	$$(eval COMMAND := hatch run dev:"$(1)")
	@$$(MAKE) run_with_log ACTION="$$ACTION" COMMAND="$$COMMAND"
endef

scripts := \
    key-check \
    analyze-spreadsheet \
    download-sheets-to-sqlite \
    generate-reports

tools := \
    format \
    lint \
    run_tests \
    pre_commit_check

$(foreach target,$(scripts),$(eval $(call run-script,$(target))))
$(foreach target,$(tools),$(eval $(call run-tool,$(target))))
