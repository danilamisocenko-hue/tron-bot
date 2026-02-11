from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import get_wallets
from chains.tron import get_trc20_usdt
from chains.ethereum import get_erc20_usdt
from chains.bsc import get_bep20_usdt
import os

ETH_API = os.getenv("ETH_API")
BSC_API = os.getenv("BSC_API")

def start_scheduler(app):
    scheduler = AsyncIOScheduler()

    async def check_wallets():
        wallets = get_wallets()
        for user_id, address, network in wallets:
            try:
                if network.lower() == "trc20":
                    txs = get_trc20_usdt(address)
                elif network.lower() == "erc20":
                    txs = get_erc20_usdt(address, ETH_API)
                elif network.lower() == "bep20":
                    txs = get_bep20_usdt(address, BSC_API)
                else:
                    continue

                total = sum(txs)
                if total > 1500:
                    await app.bot.send_message(
                        chat_id=user_id,
                        text=f"🚨 Объём за 12ч превышает 1500 USDT\n{address}\nСумма: {round(total,2)} USDT"
                    )
            except:
                pass

    scheduler.add_job(check_wallets, "interval", minutes=10)
    scheduler.start()