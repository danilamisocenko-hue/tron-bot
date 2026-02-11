from chains.tron import get_trc20_balance
from chains.ethereum import get_erc20_balance

# Универсальная функция для проверки баланса по сети
def get_balance(network, wallet_address, contract_address):
    if network == "TRC20":
        return get_trc20_balance(wallet_address, contract_address)
    elif network == "ERC20":
        return get_erc20_balance(wallet_address, contract_address)
    else:
        return 0