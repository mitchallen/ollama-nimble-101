# CLAUDE.md

Python examples for Ollama's **Nimble** decision model (https://ollama.com/library/nimble), managed
with **uv** and driven by **make**. README.md is the user-facing doc; this file covers what an agent
needs to work on the repo.

## Commands

Always go through `make` (run `make help` for the list). Most targets depend on `setup` (`uv sync`).

- `make test`: unit tests, mocked with `httpx.MockTransport`, no Ollama needed.
- `make lint format-check`: ruff. This is exactly what CI runs, so run it before committing.
- `make format`: apply ruff formatting and fixes.
- `make test-live` / `make examples`: need a local Ollama (0.35 or later) with `nimble` pulled.
  `make check` verifies both.

## Nimble is not a chat model

- Call `POST /v1/systemone`, **not** `/api/chat` or `/api/generate`. The request body is
  `{model, state, questions, keep_alive?}`. `state` can be a string, an object or an array.
- `questions` holds 1–64 named questions, each with a `type`:
  - `choice`: `criteria` is `{option: description | null}` (2–26 options). The response has
    `choice`, `probabilities` and `confidence`.
  - `noul`: a yes/no question. Optional `criteria` is `{"true": ..., "false": ...}`. The
    response's `noul` is the **probability of true**, not a bool.
  - `score`: `criteria` is a list of levels, lowest first (2–26). The response's `score` is a
    **float expected value** in `0..n-1`, not an index. Round it and look it up in `legend`
    (whose keys are strings, e.g. `legend["2"]`).
- `confidence` shows how concentrated the probabilities are. It is not a measure of accuracy.
- Limits: the prompt must fit in 8,192 tokens, and the request body in 64 KiB. Each question is
  scored independently. Nimble never produces free text.

## Layout

- `src/nimble101/client.py`: `NimbleClient.decide()` plus the `choice` / `noul` / `score`
  question builders. It returns raw response dicts on purpose, to keep the API visible. Don't
  wrap the responses in models unless asked.
- `examples/*.py`: each file is a standalone script with a `main()` and a matching make target.
  When you add an example, also add a make target, list it in `examples:` and document it in the
  README.
- `tests/test_client.py`: unit tests. Live tests are marked `@pytest.mark.integration` and are
  excluded by default through `addopts` in `pyproject.toml`.

## Configuration

- `OLLAMA_HOST` (default `http://localhost:11434`) and `NIMBLE_MODEL` (default `nimble`) are
  read by the client. The Makefile's `MODEL` variable is exported as `NIMBLE_MODEL`.
- Python 3.11 or later is required (`typing.Self`). `.python-version` pins 3.12 locally, and CI
  tests 3.11, 3.12 and 3.13.

## CI / repo

- `.github/workflows/ci.yml` runs lint, the format check and the unit tests. It does **not** run
  the integration tests, because the model is 9.5 GB.
- `astral-sh/setup-uv` publishes no floating major tag, so pin its full version (e.g.
  `@v10.2.0`). `@v10` fails to resolve.
- Dependabot opens weekly grouped PRs for uv and GitHub Actions. Security alerts and automatic
  security fixes are enabled.
- The repo is public (github.com/mitchallen/ollama-nimble-101) and MIT licensed. Never commit
  `.venv/`, tokens or `.npmrc`.
