
import os
import requests

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"].rstrip("/")
MESSAGE_ID = os.environ["DISCORD_MESSAGE_ID"]

IMAGE_PATH = "turnyro_lentele.png"


def main():
    if not os.path.isfile(IMAGE_PATH):
        raise FileNotFoundError(
            f"Nerastas paveikslelis: {IMAGE_PATH}"
        )

    url = f"{WEBHOOK_URL}/messages/{MESSAGE_ID}"

    payload = {
        "content": "🏆 **SPECAS.LT | DEAGLE 1V1 TURNYRAS**",
        "attachments": [
            {
                "id": 0,
                "filename": "turnyro_lentele.png"
            }
        ],
        "allowed_mentions": {"parse": []}
    }

    with open(IMAGE_PATH, "rb") as image:
        response = requests.patch(
            url,
            data={
                "payload_json": __import__("json").dumps(payload)
            },
            files={
                "files[0]": (
                    "turnyro_lentele.png",
                    image,
                    "image/png"
                )
            },
            timeout=30
        )

    response.raise_for_status()
    print("Discord turnyro lentele atnaujinta!")


if __name__ == "__main__":
    main()
