# Contributing

Thanks for your interest in improving **ollama-nimble-101**. Bug reports, new examples and doc
fixes are all welcome.

## Prerequisites

- [uv](https://docs.astral.sh/uv/). It installs the right Python version for you (3.11 or later).
- `make`
- For running the examples or live tests: [Ollama](https://ollama.com) 0.35 or later, and the
  model pulled with `make pull` (about 9.5 GB).

You don't need Ollama or the model to run the unit tests, lint or format checks.

## Getting started

```sh
git clone https://github.com/mitchallen/ollama-nimble-101.git
cd ollama-nimble-101
make setup      # uv sync
make test       # unit tests
make help       # every target
```

## Making a change

1. Fork the repo and create a branch from `main`.
2. Make your change.
3. Run the same checks CI runs:

   ```sh
   make format            # auto-format with ruff
   make lint format-check test
   ```

4. If you have the model locally, also run `make test-live` and any examples you touched.
5. Open a pull request with a short description of what changed and why.

CI runs lint, the format check and the unit tests on Python 3.11, 3.12 and 3.13. It doesn't run
the integration tests, because the model is too large for the runners.

## Adding an example

1. Add `examples/<name>.py` as a standalone script with a `main()` function that uses
   `NimbleClient` and the `choice` / `noul` / `score` helpers.
2. Add a `<name>` target to the `Makefile` (depending on `setup check`), and add it to the
   `examples` target and to `.PHONY`.
3. List it under "Make targets" in `README.md`.

Keep examples short and focused on one use case. Nimble only returns typed decisions, so good
examples show a real classification task, not text generation.

## Guidelines

- Keep the client thin. `NimbleClient.decide()` returns the raw response on purpose, so the
  `/v1/systemone` JSON stays visible.
- Add a unit test (using `httpx.MockTransport`) for any client change. Mark tests that need a
  running model with `@pytest.mark.integration`.
- Add dependencies with `uv add` (or `uv add --dev`) so `uv.lock` stays in sync, and commit the
  lockfile.
- Never commit secrets, `.venv/` or `.npmrc`.

## Reporting issues

Open an issue at https://github.com/mitchallen/ollama-nimble-101/issues and include your OS,
`ollama --version`, `uv --version`, and the full command and output.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
