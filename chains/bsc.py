import requests
from datetime import datetime, timedelta

USDT_BEP20 = "0x55d398326f99059fF775485246999027B3197955"

def get_bep20_usdt(address, api_key, hours=12):
    since = datetime.utcnow() - timedelta(hours=hours)
    url = "https://api.bscscan.com/api"
    params = {
        "module": "account",
        "action": "tokentx",
        "contractaddress": USDT_BEP20,
        "address": address,
        "sort": "desc",
        "apikey": api_key
    }
    r = requests.get(url, params=params)
    data = r.json().get("result", [])
    txs = []

    for tx in data:
        tx_time = datetime.utcfromtimestamp(int(tx["timeStamp"]))
        if tx_time < since:
            break
        txs.append(int(tx["value"]) / 1_000_000)
    return txs