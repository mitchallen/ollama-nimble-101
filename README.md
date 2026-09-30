# ollama-nimble-101

[![CI](https://github.com/mitchallen/ollama-nimble-101/actions/workflows/ci.yml/badge.svg)](https://github.com/mitchallen/ollama-nimble-101/actions/workflows/ci.yml)

Python examples for [Nimble](https://ollama.com/library/nimble), a 9B **decision model** from
Bespoke Labs (fine-tuned from Qwen3.5-9B) served by Ollama. It uses [uv](https://docs.astral.sh/uv/)
and `make`.

Nimble doesn't chat or write text. You send it some input plus up to 64 named questions, and it
answers each one with a typed decision, usually in under 100 ms:

| Type     | You supply                               | You get back                                        |
|----------|------------------------------------------|-----------------------------------------------------|
| `choice` | `{option: description}` (2–26 options)  | `choice`, `probabilities`, `confidence`             |
| `noul`   | a yes/no question                        | `noul`: the probability that the answer is true     |
| `score`  | ordered levels, lowest first (2–26)      | `score`: the expected level (0-based), `legend`, `probabilities` |

Questions are sent to `POST /v1/systemone` (this needs Ollama 0.35 or later).

## Quick start

```sh
make pull      # ollama pull nimble  (~9.5 GB)
make setup     # uv sync
make run       # ticket routing example
```

## Make targets

```
make help        list every target
make check       confirm Ollama is running and the model is available
make routing     ticket routing: choice + yes/no + rubric in one call
make moderation  comment moderation with yes/no thresholds
make sentiment   review sentiment with probability distributions
make examples    run all examples
make curl        call the raw endpoint with curl
make test        unit tests (mocked, no Ollama needed)
make test-live   integration test against the local model
make lint        ruff check
make format      ruff format        (make format-check only checks)
make clean       remove .venv and caches
```

`OLLAMA_HOST` (default `http://localhost:11434`) and `MODEL` (default `nimble`) can be overridden,
e.g. `make run OLLAMA_HOST=http://gpu-box:11434`.

## Using the client

```python
from nimble101 import NimbleClient, choice, noul, score

with NimbleClient() as client:
    result = client.decide(
        {"ticket": "I was charged twice. Please refund the extra payment."},
        {
            "team": choice(
                "Which team should handle this?", {"billing": "Payments", "technical": "Bugs"}
            ),
            "refund": noul("Does the customer ask for a refund?"),
            "urgency": score("How urgent is this?", ["Routine", "Soon", "Urgent"]),
        },
    )

print(result["answers"]["team"]["choice"])  # "billing"
print(result["answers"]["refund"]["noul"])  # ~0.99
print(result["answers"]["urgency"]["score"])  # 0.0 – 2.0
```

`src/nimble101/client.py` is a thin `httpx` wrapper, so the request and response JSON stay
visible. Bespoke Labs also publishes an official `typesafe-sdk` package on PyPI.

## Limitations

- Nimble can only pick from the answers you provide. It won't write explanations, nested
  JSON or quotes from the input.
- Each question is scored independently, and the prompt must fit in 8,192 tokens (the request
  body is limited to 64 KiB).
- `confidence` shows how concentrated the probabilities are. It doesn't measure whether the
  answer is correct.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
