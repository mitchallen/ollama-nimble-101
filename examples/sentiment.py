"""Classify product reviews and print the full probability distribution."""

import json

from nimble101 import NimbleClient, choice, score

REVIEWS = [
    "Battery lasts forever and the screen is gorgeous. Best phone I've owned.",
    "It's fine. Does what it says, nothing special.",
    "Stopped charging after two weeks and support never answered.",
]

QUESTIONS = {
    # None descriptions: the option names are self-explanatory
    "sentiment": choice(
        "What is the overall sentiment?",
        {
            "positive": None,
            "neutral": None,
            "negative": None,
        },
    ),
    "stars": score(
        "How many stars would this reviewer give?",
        [
            "1 star",
            "2 stars",
            "3 stars",
            "4 stars",
            "5 stars",
        ],
    ),
}


def main() -> None:
    with NimbleClient() as client:
        for review in REVIEWS:
            result = client.decide(review, QUESTIONS)
            a = result["answers"]
            print(f"\n{review}")
            print(f"  sentiment: {a['sentiment']['choice']}")
            print(f"  stars    : {a['stars']['score'] + 1:.1f} / 5")
            print(f"  probs    : {json.dumps(a['sentiment']['probabilities'], indent=None)}")
            print(f"  usage    : {result['usage']}")


if __name__ == "__main__":
    main()
