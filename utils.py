import requests
from datetime import datetime, timedelta

ETH_API = "F7R62RBETN6MUW53BV464HCX6PRF62JGQG"

# --- Получаем баланс ---
def get_trc20_balance(address):
    try:
        url = f"https://apilist.tronscan.org/api/token_trc20?limit=50&start=0&address={address}"
        resp = requests.get(url).json()
        total = 0
        for token in resp.get("data", []):
            total += int(token.get("balance", 0)) / (10 ** int(token.get("tokenDecimal", 0)))
        return total
    except:
        return 0

def get_erc20_balance(address):
    if not ETH_API:
        return 0
    try:
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={ETH_API}"
        resp = requests.get(url).json()
        if resp.get("status") != "1":
            return 0
        return int(resp["result"]) / 10**18
    except:
        return 0

# --- Получаем последние транзакции ---
def get_trc20_txs(address):
    try:
        url = f"https://apilist.tronscan.org/api/transaction?sort=-timestamp&count=true&limit=50&start=0&address={address}"
        resp = requests.get(url).json()
        txs = []
        cutoff = datetime.utcnow() - timedelta(hours=12)
        for t in resp.get("data", []):
            ts = datetime.utcfromtimestamp(t["block_timestamp"]/1000)
            if ts < cutoff:
                continue
            txs.append({
                "timestamp": ts,
                "from": t["ownerAddress"],
                "to": t["toAddress"],
                "amount": int(t.get("amount",0))/1e6,
            })
        return txs
    except:
        return []

def get_erc20_txs(address):
    if not ETH_API:
        return []
    try:
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&sort=desc&apikey={ETH_API}"
        resp = requests.get(url).json()
        txs = []
        cutoff = datetime.utcnow() - timedelta(hours=12)
        for t in resp.get("result", []):
            ts = datetime.utcfromtimestamp(int(t["timeStamp"]))
            if ts < cutoff:
                continue
            txs.append({
                "timestamp": ts,
                "from": t["from"],
                "to": t["to"],
                "amount": int(t["value"])/1e18,
            })
        return txs
    except:
        return []

# --- Проверка, биржевой ли кошелек ---
def is_exchange_wallet(txs):
    # Простая эвристика: если почти все исходящие идут на известные биржи
    exchange_addresses = [
        # можно добавить адреса популярных бирж
        "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", # пример
    ]
    outgoing = [t["to"] for t in txs]
    if not outgoing:
        return False
    if all(addr in exchange_addresses for addr in outgoing[:5]):
        return True
    return False

# --- Универсальная функция для бот.py ---
def check_wallet(wallet):
    network = wallet.get("network")
    address = wallet.get("address")
    if network == "TRC20":
        balance = get_trc20_balance(address)
        txs = get_trc20_txs(address)
    elif network == "ERC20":
        balance = get_erc20_balance(address)
        txs = get_erc20_txs(address)
    else:
        balance = 0
        txs = []
    approx_balance = balance + sum(t["amount"] for t in txs if t["to"]==address) - sum(t["amount"] for t in txs if t["from"]==address)
    exchange = is_exchange_wallet(txs)
    return {
        "balance": balance,
        "txs": txs,
        "approx_balance": approx_balance,
        "exchange": exchange
    }