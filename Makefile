BLUE='\033[0;34m'
NC='\033[0m' # No Color

test:
	@pytest

lint:
	@echo "\n${BLUE}Running Black against source and test files...${NC}\n"
	@black .
	@echo "\n${BLUE}Running Flake8 against source and test files...${NC}\n"
	@flake8 .
	@echo "\n${BLUE}Running isort against source and test files...${NC}\n"
	@isort ./**/*.py

lint-check:
	@echo "\n${BLUE}Check Black against source and test files...${NC}\n"
	@black . --check
	@echo "\n${BLUE}Check Flake8 against source and test files...${NC}\n"
	@flake8 .
	@echo "\n${BLUE}Check isort against source and test files...${NC}\n"
	@isort ./**/*.py --check-only