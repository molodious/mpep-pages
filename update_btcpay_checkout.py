#!/usr/bin/env python3
"""Update the WordPress-managed BTCPay checkout page for the 15% BTC offer."""

import os
import re
import sys

import requests
from requests.auth import HTTPBasicAuth

WP_BASE = "https://mechanicalpeexamprep.com/wp-json/wp/v2"
WP_USER = "dan"
WP_PASS = os.environ["WP_PASSWORD"]
PAGE_ID = 3636
CACHE_URL = "https://mechanicalpeexamprep.com/wp-json/elementor/v1/cache"

REPLACEMENTS = {
    "Save 10% with Bitcoin": "Save 15% with Bitcoin",
    "btcPrice: 1799.00": "btcPrice: 1699.00",
    "btcPrice: 584.10": "btcPrice: 550.00",
    "btcPrice: 359.10": "btcPrice: 339.00",
    "btcPrice: 89.10": "btcPrice: 85.00",
    "btcPrice: 539.10": "btcPrice: 509.00",
    "btcPrice: 899.10": "btcPrice: 849.00",
    "btcPrice: 1619.10": "btcPrice: 1529.00",
}


def main() -> int:
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    page_url = f"{WP_BASE}/pages/{PAGE_ID}?context=edit"
    page = requests.get(page_url, auth=auth, timeout=20)
    if page.status_code != 200:
        print(f"Failed to fetch page: HTTP {page.status_code}")
        print(page.text[:500])
        return 1

    data = page.json()
    content = data["content"]["raw"]
    updated = content
    for old, new in REPLACEMENTS.items():
        updated = updated.replace(old, new)

    if updated == content:
        print("No changes made; target strings were not found.")
        return 1

    stale = re.findall(r"Save 10%|btcPrice:\s*(1799\.00|584\.10|359\.10|89\.10|539\.10|899\.10|1619\.10)", updated)
    if stale:
        print("Refusing to update because stale BTC copy/prices remain after replacement:")
        print(stale)
        return 1

    response = requests.post(page_url, json={"content": updated}, auth=auth, timeout=30)
    if response.status_code != 200:
        print(f"Failed to update page: HTTP {response.status_code}")
        print(response.text[:1000])
        return 1

    cache = requests.delete(CACHE_URL, auth=auth, timeout=20)
    print("BTCPay checkout page updated.")
    print(f"Elementor cache cleared ({cache.status_code}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
