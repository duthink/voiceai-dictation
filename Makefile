.PHONY: install install-dev test lint selftest run clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install voiceai-dictation
	./install.sh

install-dev: ## Install with dev dependencies
	./install.sh --dev

run: ## Start the dictation daemon
	python -m voiceai

selftest: ## Run hardware/software self-test
	python -m voiceai.selftest

test: ## Run unit tests
	pytest tests/ -v

lint: ## Lint with ruff
	ruff check voiceai/ tests/

format: ## Auto-format with ruff
	ruff format voiceai/ tests/

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
