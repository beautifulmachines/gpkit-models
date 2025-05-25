.PHONY: test format install-dev

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

# Help
help:
	@echo "Available commands:"
	@echo "  install-dev       Install development dependencies"
	@echo "  test              Run all tests"
	@echo "  format            Format code with isort and black"
	@echo "  help              Show this help message" 
