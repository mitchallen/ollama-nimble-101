import json

import httpx
import pytest

from nimble101 import NimbleClient, choice, noul, score


def test_question_builders():
    assert choice("Q?", {"a": None}) == {
        "type": "choice",
        "instructions": "Q?",
        "criteria": {"a": None},
    }
    assert noul("Q?") == {"type": "noul", "instructions": "Q?"}
    assert noul("Q?", true="yes")["criteria"] == {"true": "yes", "false": None}
    assert score("Q?", ["lo", "hi"])["criteria"] == ["lo", "hi"]


def test_decide_posts_expected_body():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content)
        return httpx.Response(
            200, json={"model": "nimble", "answers": {"x": {"type": "noul", "noul": 0.9}}}
        )

    with NimbleClient(host="localhost:11434", transport=httpx.MockTransport(handler)) as client:
        result = client.decide("text", {"x": noul("Q?")}, keep_alive="5m")

    assert seen["path"] == "/v1/systemone"
    assert seen["body"] == {
        "model": "nimble",
        "state": "text",
        "questions": {"x": {"type": "noul", "instructions": "Q?"}},
        "keep_alive": "5m",
    }
    assert result["answers"]["x"]["noul"] == 0.9


def test_decide_raises_on_http_error():
    transport = httpx.MockTransport(
        lambda r: httpx.Response(404, json={"error": "model not found"})
    )
    with NimbleClient(transport=transport) as client, pytest.raises(httpx.HTTPStatusError):
        client.decide("text", {"x": noul("Q?")})


@pytest.mark.integration
def test_live_billing_ticket():
    with NimbleClient() as client:
        result = client.decide(
            "I was charged twice. Please refund the extra payment.",
            {"team": choice("Which team?", {"billing": "Payments", "technical": "Bugs"})},
        )
    assert result["answers"]["team"]["choice"] == "billing"
