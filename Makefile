GOINFRE_CACHE=$(HOME)/goinfre/call_me_maybe_cache
GOINFRE_VENV=$(HOME)/goinfre/call_me_maybe_venv

run:
	@HF_HOME=$(GOINFRE_CACHE)/huggingface \
	UV_CACHE_DIR=$(GOINFRE_CACHE)/uv \
	UV_PROJECT_ENVIRONMENT=$(GOINFRE_VENV) \
	uv run python -m src

install:
	@mkdir -p $(GOINFRE_CACHE)/huggingface
	@mkdir -p $(GOINFRE_CACHE)/uv
	@HF_HOME=$(GOINFRE_CACHE)/huggingface \
	UV_CACHE_DIR=$(GOINFRE_CACHE)/uv \
	UV_PROJECT_ENVIRONMENT=$(GOINFRE_VENV) \
	uv sync

debug:
	@HF_HOME=$(GOINFRE_CACHE)/huggingface \
	UV_CACHE_DIR=$(GOINFRE_CACHE)/uv \
	UV_PROJECT_ENVIRONMENT=$(GOINFRE_VENV) \
	uv run python -m pdb -m src

clean:
	@rm -rf .mypy_cache src/__pycache__ src/tools/__pycache__ llm_sdk/llm_sdk/__pycache__
	@rm -rf data/output

fclean:
	@rm -rf $(GOINFRE_CACHE)
	@rm -rf $(GOINFRE_VENV)

lint:
	@HF_HOME=$(GOINFRE_CACHE)/huggingface \
	UV_CACHE_DIR=$(GOINFRE_CACHE)/uv \
	UV_PROJECT_ENVIRONMENT=$(GOINFRE_VENV) \
	uv run flake8 src
	
	@HF_HOME=$(GOINFRE_CACHE)/huggingface \
	UV_CACHE_DIR=$(GOINFRE_CACHE)/uv \
	UV_PROJECT_ENVIRONMENT=$(GOINFRE_VENV) \
	mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs \
	--exclude=llm_sdk

.PHONY: install run fclean clean lint