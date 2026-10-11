
import os
import json
import requests

PROJECT_ID = "specas-deagle-turnyras"
DOCUMENT = "tournaments/deagle1v1"

FIREBASE_URL = (
    f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}"
    f"/databases/(default)/documents/{DOCUMENT}"
)

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


def get_tournament():
    response = requests.get(FIREBASE_URL, timeout=20)
    response.raise_for_status()

    fields = response.json()["fields"]

    return {
        "bracket": json.loads(fields["publishedBracket"]["stringValue"]),
        "published_at": fields.get("publishedAt", {}).get("integerValue"),
    }


def format_bracket(rounds):
    lines = ["🏆 **SPECAS.LT – DEAGLE 1V1 TURNYRAS**", ""]

    round_names = [
        "Aštuntfinalis",
        "Ketvirtfinalis",
        "Pusfinalis",
        "Finalas",
    ]

    for index, matches in enumerate(rounds):
        name = round_names[index] if index < len(round_names) else f"Etapas {index + 1}"
        lines.append(f"**{name}**")

        for match in matches:
            if not isinstance(match, list) or len(match) < 2:
                continue

            first, second = match[:2]
            name1 = first.get("name", "Laukiama") or "Laukiama"
            name2 = second.get("name", "Laukiama") or "Laukiama"
            score1 = first.get("score", "")
            score2 = second.get("score", "")

            lines.append(f"• {name1} **{score1} : {score2}** {name2}")

        lines.append("")

    return "\n".join(lines)


def main():
    tournament = get_tournament()
    message = format_bracket(tournament["bracket"])

    # Kol kas tik patikriname, ar rezultatai nuskaitomi.
    # Discord pranešimų dar nesiunčiame.
    print(message)


if __name__ == "__main__":
    main()
