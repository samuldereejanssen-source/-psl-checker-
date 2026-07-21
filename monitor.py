"""
PSL Drop Checker
----------------
Watches PSL Source and STR Marketplace for NEW listings appearing on
teams you choose (see teams.json), and pings Discord the moment one shows up.

You do not need to understand this file to use it. See README.md for setup.
"""

import json
import os
import time
from pathlib import Path

import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
TEAMS_FILE = Path(__file__).parent / "teams.json"
STATE_FILE = Path(__file__).parent / "state.json"
REQUEST_TIMEOUT = 15

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}


def load_teams():
    return json.loads(TEAMS_FILE.read_text())


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def fetch_pslsource_listings(team_id: int):
    """PSL Source's internal data feed. Returns a list of listing dicts."""
    url = f"https://www.pslsource.com/inventory/{team_id}"
    resp = requests.post(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    payload = resp.json()
    return payload.get("data", [])


def fetch_strmarketplace_listings(subdomain: str, code: str):
    """STR Marketplace's internal data feed. Returns a list of listing dicts."""
    url = f"https://{subdomain}.strmarketplace.com/WebServices/json/{code}/data.json"
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def describe_pslsource_listing(listing: dict) -> str:
    section = listing.get("section_number") or listing.get("section", {}).get("name", "?")
    row = listing.get("row_name") or listing.get("row", {}).get("name", "?")
    seats = listing.get("amount_of_seats", "?")
    price = listing.get("total_asking_price", "?")
    per_seat = listing.get("price_per_seat", "?")
    return f"Section {section}, Row {row} — {seats} seat(s) — ${price} (${per_seat}/seat)"


def describe_str_listing(listing: dict) -> str:
    section = listing.get("Section") or listing.get("section") or "?"
    row = listing.get("Row") or listing.get("row") or "?"
    price = listing.get("Price") or listing.get("total_price") or "?"
    return f"Section {section}, Row {row} — {price}"


def send_discord_alert(site: str, team_name: str, description: str, listing_id):
    if not DISCORD_WEBHOOK_URL:
        print(f"  [warn] No DISCORD_WEBHOOK_URL set - skipping alert for {team_name}.")
        return
    content = (
        f"🆕 **New PSL listing!**\n"
        f"**{team_name}** ({site})\n"
        f"{description}\n"
        f"Listing ID: {listing_id}"
    )
    try:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": content}, timeout=10)
    except requests.RequestException as e:
        print(f"  [error] Failed to send Discord alert: {e}")


def process_team(site: str, team_name: str, listings: list, describe_fn, state: dict):
    key = f"{site}:{team_name}"
    is_first_time_seeing_this_team = key not in state
    seen_ids = set(state.get(key, []))
    current_ids = set()
    new_count = 0

    for listing in listings:
        listing_id = listing.get("id")
        if listing_id is None:
            continue
        current_ids.add(listing_id)
        if listing_id not in seen_ids:
            if is_first_time_seeing_this_team:
                print(f"  [baseline] {team_name}: recording listing {listing_id}")
            else:
                description = describe_fn(listing)
                print(f"  [new] {team_name}: {description}")
                send_discord_alert(site, team_name, description, listing_id)
                new_count += 1

    state[key] = list(current_ids)
    return new_count


def main():
    teams = load_teams()
    state = load_state()
    total_new = 0

    print("Checking PSL Source teams...")
    for team in teams.get("pslsource_teams", []):
        try:
            listings = fetch_pslsource_listings(team["team_id"])
            total_new += process_team(
                "PSL Source", team["name"], listings, describe_pslsource_listing, state
            )
        except requests.RequestException as e:
            print(f"  [error] {team['name']} (PSL Source): {e}")
        time.sleep(1.5)

    print("Checking STR Marketplace teams...")
    for team in teams.get("strmarketplace_teams", []):
        try:
            listings = fetch_strmarketplace_listings(team["subdomain"], team["code"])
            total_new += process_team(
                "STR Marketplace", team["name"], listings, describe_str_listing, state
            )
        except requests.RequestException as e:
            print(f"  [error] {team['name']} (STR Marketplace): {e}")
        time.sleep(1.5)

    save_state(state)
    print(f"Done. {total_new} new listing(s) found this run.")


if __name__ == "__main__":
    main()
