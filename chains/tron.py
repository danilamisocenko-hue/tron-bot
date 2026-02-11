import requests
from datetime import datetime, timedelta

USDT_TRON = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

def get_trc20_usdt(address, hours=12):
    since = int((datetime.utcnow() - timedelta(hours=hours)).timestamp() * 1000)
    url = "https://apilist.tronscan.org/api/token_trc20/transfers"
    start = 0
    txs = []

    while True:
        params = {
            "relatedAddress": address,
            "contract_address": USDT_TRON,
            "limit": 50,
            "start": start,
            "sort": "-timestamp"
        }

        r = requests.get(url, params=params)
        data = r.json().get("token_transfers", [])

        if not data:
            break

        for tx in data:
            if tx["block_ts"] < since:
                return txs
            txs.append(int(tx["quant"]) / 1_000_000)

        start += 50

    return txs