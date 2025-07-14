RED    := $(shell tput -Txterm setaf 1)
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
CYAN   := $(shell tput -Txterm setaf 6)
RESET  := $(shell tput -Txterm sgr0)

.PHONY: all
all: help

## 🛠️  Setup
.PHONY: setup
setup: ## sets up the project.
	@echo "${CYAN}🔧 Setting up project...${RESET}"
	@echo "TODO"
	@echo "${GREEN}✅ Project setup completed!${RESET}"

## 🔍 Linting 
.PHONY: lint
lint: ## runs linters for all packages.
	@make \
		lint/ruff-check \
		lint/ruff-format-check \
		lint/mypy || \
	(echo "❗ Linting failed. Try running 'make lint/fix' to resolve issues." && exit 1)

.PHONY: lint/fix
lint/fix: lint/ruff lint/ruff-format lint/mypy ## Run all the linters and fix the issues

.PHONY: lint/ruff
lint/ruff: ## Use ruff on the project
	@echo "🔎 Performing static code analysis"
	@uv run ruff check --fix
	@echo "${GREEN}Static code analysis completed successfully.${RESET}"

.PHONY: lint/ruff-check
lint/ruff-check: ## Check the project with ruff
	@echo "🔎 Checking the project with ruff"
	@uv run ruff check
	@echo "${GREEN}Project checked with ruff successfully.${RESET}"


.PHONY: lint/ruff-format-check
lint/mypy: ## Run mypy on the project 
	@echo "🔎 Running mypy"
	@uv run mypy walking_on_sunshine/
	@echo "${GREEN}dmypy completed successfully.${RESET}"

.PHONY: lint/ruff-format
lint/ruff-format: ## Format the code of the project
	@echo "✨ Applying code formatting with ruff"
	@uv run ruff format ./walking_on_sunshine
	@echo "${GREEN}Code formatted successfully.${RESET}"

.PHONY: lint/ruff-format-check
lint/ruff-format-check: ## Check the code formatting of the project
	@echo "🔍 Checking code formatting with ruff"
	@uv run ruff format --check
	@echo "${GREEN}Code formatting check completed successfully.${RESET}"

## 🧪 Testing
.PHONY: test
test: ## runs tests for all packages.
	@echo "${CYAN}🧪 Running tests...${RESET}"
	@uv run pytest
	@echo "${GREEN}✅ Tests completed!${RESET}"

## 🧹 Cleaning
.PHONY: clean
clean: ## cleans up the whole project.
	@echo "${CYAN}🧹 Cleaning up project...${RESET}"
	@echo "${GREEN}✅ Project cleaned successfully!${RESET}"

.PHONY: help
help:
	@echo ''
	@echo '📋 ${CYAN}Usage:${RESET}'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo '📋 ${CYAN}Targets:${RESET}'
	@awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[[:graph:]]+:.*?##.*$$/) {printf "    ${YELLOW}%-30s${GREEN}%s${RESET}\n", $$1, $$2} \
		else if (/^## .*$$/) {printf "  ${CYAN}%s${RESET}\n", substr($$1,4)} \
		}' $(MAKEFILE_LIST)
