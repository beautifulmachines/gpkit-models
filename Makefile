.PHONY: clean check-clean test coverage lint format release

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

# Releasing
release: check-clean  # Cut a release: make release V=x.y.z
	@if [ -z "$(V)" ]; then \
		echo "Usage: make release V=x.y.z"; \
		exit 1; \
	fi
	@echo "$(V)" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$$' || { \
		echo "V must look like x.y.z (got '$(V)')"; \
		exit 1; \
	}
	@git fetch origin main --quiet
	@if [ "$$(git rev-parse HEAD)" != "$$(git rev-parse origin/main)" ]; then \
		echo "HEAD is not up to date with origin/main. Pull or push first."; \
		exit 1; \
	fi
	gh release create v$(V) --generate-notes


# Help
help:
	@echo "Available commands:"
	@echo "  lint              Run lint checks"
	@echo "  format            Format code with ruff"
	@echo "  test              Run tests with pytest"
	@echo "  coverage          Run tests with coverage reporting"
	@echo "  clean             Clean build artifacts"
	@echo "  check-clean       Check no uncommitted changes"
	@echo "  release           Cut a release (make release V=x.y.z)"
	@echo "  help              Show this help message"
