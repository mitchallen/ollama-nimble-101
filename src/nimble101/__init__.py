"""Minimal client for Ollama's Nimble decision model."""

from nimble101.client import NimbleClient, choice, noul, score

__all__ = ["NimbleClient", "choice", "noul", "score"]
