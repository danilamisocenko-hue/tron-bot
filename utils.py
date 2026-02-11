def detect_chain(address: str):
    if address.startswith("T") and len(address) == 34:
        return "TRC20"
    if address.startswith("0x") and len(address) == 42:
        return "EVM"
    return None