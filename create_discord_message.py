
import os
import requests

webhook = os.environ["DISCORD_WEBHOOK_URL"]

response = requests.post(
    webhook + "?wait=true",
    json={"content": "🏆 SPECAS.LT turnyro lentelė – ruošiama..."},
    timeout=30
)
response.raise_for_status()

print("NAUJAS_DISCORD_MESSAGE_ID:", response.json()["id"])
