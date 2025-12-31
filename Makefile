web:
	@echo "Running Web App..."
	@python -m web.app
dev:
	@echo "Running internship sync pipeline..."
	@python -m src.main
all:
	@./scripts/run.sh
