import requests
import os

ETH_API = os.environ.get("ETH_API")

def get_erc20_balance(wallet_address, contract_address):
    if not ETH_API:
        print("ETH_API не установлен")
        return 0

    url = (
        f"https://api.etherscan.io/api"
        f"?module=account"
        f"&action=tokenbalance"
        f"&contractaddress={contract_address}"
        f"&address={wallet_address}"
        f"&tag=latest"
        f"&apikey={ETH_API}"
    )

    try:
        response = requests.get(url).json()

        if response.get("status") != "1":
            print("Ошибка Etherscan:", response)
            return 0

        balance = int(response["result"]) / 10**18
        return balance

    except Exception as e:
        print("ERC20 Error:", e)
        return 0