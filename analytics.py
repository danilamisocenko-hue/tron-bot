def summarize(txs):
    return {
        "count": len(txs),
        "total": round(sum(txs), 2)
    }