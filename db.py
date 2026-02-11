import json
import os

WALLETS_FILE = "wallets.json"

def load_wallets():
    if not os.path.exists(WALLETS_FILE):
        with open(WALLETS_FILE, "w") as f:
            json.dump([], f)
    with open(WALLETS_FILE, "r") as f:
        return json.load(f)

def add_wallet(wallet):
    wallets = load_wallets()
    for w in wallets:
        if w["network"] == wallet["network"] and w["address"] == wallet["address"]:
            return False
    wallets.append(wallet)
    with open(WALLETS_FILE, "w") as f:
        json.dump(wallets, f, indent=4)
    return True