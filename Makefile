.PHONY: dev test lint migrate build clean train

train:
	@echo "Training LightGBM phishing detection model..."
	python backend/app/ml/train.py

migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

dev:
	@echo "Starting all services..."
	docker-compose up

dev-build:
	@echo "Building and starting all services..."
	docker-compose up --build

test:
	@echo "Running backend tests..."
	cd backend && pytest --cov=app --cov-report=html
	@echo "Running dashboard tests..."
	cd dashboard && npm test

lint:
	@echo "Linting backend..."
	cd backend && ruff check app/
	cd backend && mypy app/
	@echo "Linting dashboard..."
	cd dashboard && npm run lint

build:
	@echo "Building Docker images..."
	docker-compose build

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf backend/app/ml/models/*.pkl

setup: train migrate
	@echo "Setup complete! Run 'make dev' to start the application."
