import os

# One switch for the island: no telemetry, no update checks.
OFFLINE = os.environ.get("PARROT_OFFLINE") == "1"
PORT = int(os.environ.get("PARROT_PORT", "8600"))
