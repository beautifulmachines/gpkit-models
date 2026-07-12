.PHONY: clean check-clean test coverage lint format

# Code quality
lint:
	uv run ruff check gpkitmodels

# Code formatting
format:
	uv run ruff format gpkitmodels
	uv run ruff check --select I --fix gpkitmodels

# Testing
test:  # Run tests with pytest
	uv run pytest -v

coverage:  # Run tests with coverage reporting
	uv run pytest --cov=gpkitmodels --cov-report=term-missing

# Cleanup
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

check-clean:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Found uncommitted changes:"; \
		git status --porcelain; \
		exit 1; \
	else \
		echo "Working directory is clean."; \
	fi

# Help
help:
	@echo "Available commands:"
	@echo "  lint              Run lint checks"
	@echo "  format            Format code with ruff"
	@echo "  test              Run tests with pytest"
	@echo "  coverage          Run tests with coverage reporting"
	@echo "  clean             Clean build artifacts"
	@echo "  check-clean       Check no uncommitted changes"
	@echo "  help              Show this help message"
