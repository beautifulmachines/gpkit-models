.PHONY: test format install-dev install-lint install-test check-clean

# Install development dependencies
install-dev:
	pip install -e .[dev]

install-lint:
	pip install .[lint]

install-test:
	pip install .[test]

# Run all tests
test:
	python -c "from gpkit.tests.from_paths import run; run()"
	# ./researchmodeltests.sh

# Format code using isort and black
format:
	isort --profile black gpkitmodels
	black gpkitmodels

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
	@echo "  install-dev       Editable install for local dev"
	@echo "  install-lint      Install with linting tools for CI"
	@echo "  install-test      Install with testing tools for CI"
	@echo "  test              Run all tests"
	@echo "  format            Format code with isort and black"
	@echo "  check-clean       Check no uncommitted changes"
	@echo "  help              Show this help message" 
