"""Persistent storage for whitelist, trucks, and vehicle types (JSON files)."""
import json
import logging
import shutil
import threading
from pathlib import Path
from typing import Any

from . import config

_lock = threading.Lock()
log = logging.getLogger(__name__)


def ensure_data_files() -> None:
    """Create data/ files from data_defaults/ on first run.

    Used on cloud hosts where the persistent volume starts empty.
    Existing files are never overwritten.
    """
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("trucks.json", "vehicle_types.json", "whitelist.json"):
        target = config.DATA_DIR / name
        if target.exists():
            continue
        default = config.DATA_DEFAULTS_DIR / name
        if default.exists():
            shutil.copy(default, target)
            log.info("Initialized %s from defaults", name)
        else:
            target.write_text("{}" if name == "whitelist.json" else "[]", encoding="utf-8")


def bootstrap_admin_if_empty() -> None:
    """If whitelist has no admins AND env vars are set, add the bootstrap admin."""
    if not config.INITIAL_ADMIN_ID:
        return
    try:
        uid = int(config.INITIAL_ADMIN_ID)
    except ValueError:
        log.warning("INITIAL_ADMIN_ID is not numeric: %r — skipping bootstrap", config.INITIAL_ADMIN_ID)
        return
    wl = load_whitelist()
    if wl.get("admins"):
        return
    add_user(uid, config.INITIAL_ADMIN_NAME, as_admin=True)
    log.info("Bootstrapped initial admin %s (%s)", config.INITIAL_ADMIN_NAME, uid)


def _read(path: Path) -> Any:
    with _lock:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


def _write(path: Path, data: Any) -> None:
    with _lock:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp.replace(path)


# ---------- Whitelist ----------

def load_whitelist() -> dict:
    return _read(config.WHITELIST_FILE)


def is_user(user_id: int) -> bool:
    wl = load_whitelist()
    ids = {u["id"] for u in wl["users"]} | {a["id"] for a in wl["admins"]}
    return user_id in ids


def is_admin(user_id: int) -> bool:
    wl = load_whitelist()
    return any(a["id"] == user_id for a in wl["admins"])


def get_user(user_id: int) -> dict | None:
    """Return the whitelist entry for this user (admin or regular), or None."""
    wl = load_whitelist()
    for entry in wl["admins"] + wl["users"]:
        if entry["id"] == user_id:
            return entry
    return None


def add_user(user_id: int, name: str, as_admin: bool = False) -> None:
    wl = load_whitelist()
    key = "admins" if as_admin else "users"
    # preserve phone if the user already exists
    existing = get_user(user_id) or {}
    phone = existing.get("phone", "")
    wl["users"] = [u for u in wl["users"] if u["id"] != user_id]
    wl["admins"] = [a for a in wl["admins"] if a["id"] != user_id]
    entry = {"id": user_id, "name": name}
    if phone:
        entry["phone"] = phone
    wl[key].append(entry)
    _write(config.WHITELIST_FILE, wl)


def set_phone(user_id: int, phone: str) -> bool:
    """Save the phone number on the whitelist entry. Returns True if saved."""
    wl = load_whitelist()
    for bucket in ("admins", "users"):
        for entry in wl[bucket]:
            if entry["id"] == user_id:
                entry["phone"] = phone
                _write(config.WHITELIST_FILE, wl)
                return True
    return False


def get_phone(user_id: int) -> str:
    entry = get_user(user_id)
    return (entry or {}).get("phone", "")


def remove_user(user_id: int) -> bool:
    wl = load_whitelist()
    before = len(wl["users"]) + len(wl["admins"])
    wl["users"] = [u for u in wl["users"] if u["id"] != user_id]
    wl["admins"] = [a for a in wl["admins"] if a["id"] != user_id]
    after = len(wl["users"]) + len(wl["admins"])
    if before == after:
        return False
    _write(config.WHITELIST_FILE, wl)
    return True


# ---------- Trucks ----------

def load_trucks() -> list[dict]:
    return _read(config.TRUCKS_FILE)


def add_truck(plate: str) -> dict:
    trucks = load_trucks()
    if any(t["plate"] == plate for t in trucks):
        return next(t for t in trucks if t["plate"] == plate)
    next_no = max((t["no"] for t in trucks), default=0) + 1
    entry = {"no": next_no, "plate": plate}
    trucks.append(entry)
    _write(config.TRUCKS_FILE, trucks)
    return entry


def remove_truck(plate: str) -> bool:
    trucks = load_trucks()
    new = [t for t in trucks if t["plate"] != plate]
    if len(new) == len(trucks):
        return False
    _write(config.TRUCKS_FILE, new)
    return True


# ---------- Vehicle types ----------

def load_vehicle_types() -> list[str]:
    return _read(config.VEHICLE_TYPES_FILE)


def add_vehicle_type(name: str) -> bool:
    types = load_vehicle_types()
    if name in types:
        return False
    types.append(name)
    _write(config.VEHICLE_TYPES_FILE, types)
    return True


def remove_vehicle_type(name: str) -> bool:
    types = load_vehicle_types()
    if name not in types:
        return False
    types.remove(name)
    _write(config.VEHICLE_TYPES_FILE, types)
    return True
