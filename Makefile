MODEL       ?= nimble
OLLAMA_HOST ?= http://localhost:11434
export OLLAMA_HOST
export NIMBLE_MODEL := $(MODEL)

.DEFAULT_GOAL := help
.PHONY: help setup pull check run routing moderation sentiment examples curl test test-live lint format format-check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

setup: ## Create .venv and install dependencies with uv
	uv sync

pull: ## Download the nimble model (~9.5 GB, needs Ollama >= 0.35)
	ollama pull $(MODEL)

check: ## Verify Ollama is running and the model is available
	@curl -sf $(OLLAMA_HOST)/api/version >/dev/null || { echo "Ollama not reachable at $(OLLAMA_HOST) - start it with 'ollama serve'"; exit 1; }
	@ollama show $(MODEL) >/dev/null 2>&1 || { echo "Model '$(MODEL)' not found - run 'make pull'"; exit 1; }
	@echo "Ollama $$(ollama --version | awk '{print $$NF}') is up and '$(MODEL)' is available"

run: routing ## Run the default example (ticket routing)

routing: setup check ## Ticket routing: choice + yes/no + rubric in one call
	uv run python examples/ticket_routing.py

moderation: setup check ## Comment moderation with yes/no thresholds
	uv run python examples/moderation.py

sentiment: setup check ## Review sentiment with probability distributions
	uv run python examples/sentiment.py

examples: routing moderation sentiment ## Run every example

curl: check ## Call /v1/systemone directly with curl
	curl -s $(OLLAMA_HOST)/v1/systemone -d '{ \
	  "model": "$(MODEL)", \
	  "state": "I was charged twice. Please refund the extra payment.", \
	  "questions": { "team": { "type": "choice", \
	    "instructions": "Which team should handle this?", \
	    "criteria": {"billing": "Payments", "technical": "Bugs"} } } }' | python3 -m json.tool

test: setup ## Run unit tests (no Ollama needed)
	uv run pytest

test-live: setup check ## Run integration tests against the local model
	uv run pytest -m integration

lint: setup ## Lint with ruff
	uv run ruff check .

format-check: setup ## Check formatting without changing files
	uv run ruff format --check .

format: setup ## Format with ruff
	uv run ruff format .
	uv run ruff check --fix .

clean: ## Remove the venv and caches
	rm -rf .venv .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
