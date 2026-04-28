.PHONY: help build up down logs shell clean

help: ## Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build the Docker image
	docker-compose build

up: ## Start the application
	docker-compose up -d

down: ## Stop the application
	docker-compose down

logs: ## Show application logs
	docker-compose logs -f backend

shell: ## Open a shell in the container
	docker-compose exec backend bash

clean: ## Remove Docker images and containers
	docker-compose down -v --rmi all

restart: ## Restart the application
	docker-compose restart

dev: ## Start in development mode with hot reload
	docker-compose up --build
