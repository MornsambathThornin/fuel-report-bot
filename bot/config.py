"""Loads environment variables and exposes app-wide settings."""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")

# Two ways to provide service account credentials:
#   1) GOOGLE_SERVICE_ACCOUNT_JSON — full JSON content (preferred for cloud hosts)
#   2) GOOGLE_SERVICE_ACCOUNT_FILE — path to JSON file (preferred for local)
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "GOOGLE_SERVICE_ACCOUNT_FILE", str(ROOT / "service_account.json")
)

COMPANY_NAME_KH = os.getenv(
    "COMPANY_NAME_KH",
    "ក្រុមហ៊ុន អេកូ អ៊ែតស៍ & ហ្រ្គីន (អ៊ី អេ ជី)",
)
TIMEZONE = os.getenv("TIMEZONE", "Asia/Phnom_Penh")

# One-shot bootstrap: if whitelist is empty AND these are set, the bot
# auto-adds this account as the first admin on startup.
INITIAL_ADMIN_ID = os.getenv("INITIAL_ADMIN_ID", "")
INITIAL_ADMIN_NAME = os.getenv("INITIAL_ADMIN_NAME", "Admin")

DATA_DIR = ROOT / "data"
DATA_DEFAULTS_DIR = ROOT / "data_defaults"
TRUCKS_FILE = DATA_DIR / "trucks.json"
VEHICLE_TYPES_FILE = DATA_DIR / "vehicle_types.json"
WHITELIST_FILE = DATA_DIR / "whitelist.json"


def assert_ready() -> None:
    """Raise a clear error if required env vars are missing."""
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not GOOGLE_SHEET_ID:
        missing.append("GOOGLE_SHEET_ID")
    if not GOOGLE_SERVICE_ACCOUNT_JSON and not Path(GOOGLE_SERVICE_ACCOUNT_FILE).exists():
        missing.append(
            "service account credentials "
            f"(set GOOGLE_SERVICE_ACCOUNT_JSON env var, or place file at {GOOGLE_SERVICE_ACCOUNT_FILE})"
        )
    if missing:
        raise RuntimeError(
            "Missing configuration: " + ", ".join(missing) +
            ". See README.md for setup steps."
        )
