.PHONY: test format install-dev check-clean

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

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
	@echo "  install-dev       Install development dependencies"
	@echo "  test              Run all tests"
	@echo "  format            Format code with isort and black"
	@echo "  check-clean       Check no uncommitted changes"
	@echo "  help              Show this help message" 
