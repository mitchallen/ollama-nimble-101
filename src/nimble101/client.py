"""Thin wrapper around Ollama's /v1/systemone endpoint.

Nimble doesn't generate free text. You give it some input (`state`) and up to
64 named questions, and it answers each one with a typed decision:

  choice -> picks one of the keys you supply
  noul   -> probability that a statement is true (0.0 - 1.0)
  score  -> expected level on an ordered rubric (0 .. len(levels) - 1)
"""

from __future__ import annotations

import os
from typing import Any, Self

import httpx

DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.environ.get("NIMBLE_MODEL", "nimble")


def choice(instructions: str, criteria: dict[str, str | None]) -> dict[str, Any]:
    """Pick one option. Use None as a description for self-explanatory keys."""
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def noul(instructions: str, true: str | None = None, false: str | None = None) -> dict[str, Any]:
    """Yes/no question, answered as a probability of 'true'."""
    q: dict[str, Any] = {"type": "noul", "instructions": instructions}
    if true or false:
        q["criteria"] = {"true": true, "false": false}
    return q


def score(instructions: str, levels: list[str]) -> dict[str, Any]:
    """Rubric score. List levels lowest first; they are numbered from 0."""
    return {"type": "score", "instructions": instructions, "criteria": levels}


class NimbleClient:
    def __init__(
        self,
        host: str = DEFAULT_HOST,
        model: str = DEFAULT_MODEL,
        timeout: float = 120.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"
        self.model = model
        self._http = httpx.Client(base_url=host, timeout=timeout, transport=transport)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        self._http.close()

    def decide(
        self,
        state: str | dict[str, Any] | list[Any],
        questions: dict[str, dict[str, Any]],
        keep_alive: str | None = None,
    ) -> dict[str, Any]:
        """Ask Nimble one or more questions about `state`. Returns the raw response."""
        body: dict[str, Any] = {"model": self.model, "state": state, "questions": questions}
        if keep_alive is not None:
            body["keep_alive"] = keep_alive
        resp = self._http.post("/v1/systemone", json=body)
        resp.raise_for_status()
        return resp.json()
