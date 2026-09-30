"""Route support tickets: one call answers a choice, a yes/no and a rubric question."""

from nimble101 import NimbleClient, choice, noul, score

TICKETS = [
    "I was charged twice this month. Please refund the extra payment.",
    "The app crashes every time I log in since yesterday's update. My whole team is blocked!",
    "Do you have a dark mode? Just curious, no rush.",
    "Your API returns 500 on /v2/orders and our checkout is down. We will cancel if not fixed.",
]

QUESTIONS = {
    "team": choice(
        "Which team should handle this ticket?",
        {
            "billing": "Payments, invoices and refunds",
            "technical": "Bugs, outages and integrations",
            "product": "Feature requests and general questions",
        },
    ),
    "refund": noul("Does the customer explicitly ask for a refund?"),
    "churn_risk": noul("Does the customer threaten to cancel or leave?"),
    "urgency": score("How urgent is this ticket?", ["Routine", "Soon", "Urgent"]),
}


def main() -> None:
    with NimbleClient() as client:
        for ticket in TICKETS:
            result = client.decide({"ticket": ticket}, QUESTIONS)
            a = result["answers"]
            urgency = a["urgency"]
            level = urgency["legend"][str(round(urgency["score"]))]
            print(f"\n{ticket}")
            print(
                f"  team       : {a['team']['choice']} (confidence {a['team']['confidence']:.2f})"
            )
            print(f"  refund?    : {a['refund']['noul']:.2f}")
            print(f"  churn risk : {a['churn_risk']['noul']:.2f}")
            print(f"  urgency    : {urgency['score']:.2f} -> {level}")


if __name__ == "__main__":
    main()
