import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from utils import check_wallet
from db import load_wallets, add_wallet

# ===== Настройки =====
TOKEN = "8286019893:AAGsXwsWPtdjv0FJvBim4-gfnMCTAokAZxY"
CHAT_ID = "8286019893"

# ===== Клавиатуры =====
main_keyboard = ReplyKeyboardMarkup(
    [["📘 FAQ"], ["🔎 Проверка баланса"], ["➕ Добавить кошелек"]],
    resize_keyboard=True
)
back_keyboard = ReplyKeyboardMarkup([["⬅ Назад"]], resize_keyboard=True)
network_keyboard = ReplyKeyboardMarkup([["TRC20", "ERC20"]], resize_keyboard=True)

# ===== Состояние пользователя =====
user_state = {}  # user_id -> {"step": "check_network/add_network/check_address/add_address", "network": "TRC20/ERC20"}

# ===== Предыдущие балансы для мониторинга =====
previous_balances = {}  # key = f"{network}_{address}" -> float

# ===== Команды =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:", reply_markup=main_keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # ===== FAQ =====
    if text == "📘 FAQ":
        await update.message.reply_text(
            "Чекер нужен для проверки кошельков.\nПоддерживаемые сети: TRC20, ERC20",
            reply_markup=back_keyboard
        )
        return

    # ===== Проверка баланса =====
    if text == "🔎 Проверка баланса":
        user_state[user_id] = {"step": "check_network"}
        await update.message.reply_text("Выберите сеть для проверки баланса:", reply_markup=network_keyboard)
        return

    # ===== Добавить кошелек =====
    if text == "➕ Добавить кошелек":
        user_state[user_id] = {"step": "add_network"}
        await update.message.reply_text("Выберите сеть для добавления кошелька:", reply_markup=network_keyboard)
        return

    # ===== Назад =====
    if text == "⬅ Назад":
        user_state.pop(user_id, None)
        await update.message.reply_text("Главное меню:", reply_markup=main_keyboard)
        return

    # ===== Выбор сети для проверки =====
    if user_id in user_state and user_state[user_id].get("step") == "check_network":
        if text not in ["TRC20", "ERC20"]:
            await update.message.reply_text("Выберите TRC20 или ERC20", reply_markup=network_keyboard)
            return
        user_state[user_id]["step"] = "check_address"
        user_state[user_id]["network"] = text
        await update.message.reply_text(f"Введите адрес кошелька для сети {text}:", reply_markup=back_keyboard)
        return

    # ===== Ввод адреса для проверки =====
    if user_id in user_state and user_state[user_id].get("step") == "check_address":
        network = user_state[user_id]["network"]
        address = text.strip()
        wallet = {"network": network.upper(), "address": address}
        info = check_wallet(wallet)
        msg = f"Адрес: {address}\n"
        msg += f"Баланс: {info['balance']}\n"
        msg += f"Примерный баланс: {info['approx_balance']}\n"
        msg += f"Биржевой: {'Да' if info['exchange'] else 'Нет'}\n"
        msg += "Последние транзакции (12ч):\n"
        for t in info['txs'][:5]:
            direction = "➡" if t["from"] == address else "⬅"
            msg += f"{direction} {t['amount']} | {t['timestamp']}\n"
        user_state.pop(user_id, None)
        await update.message.reply_text(msg, reply_markup=main_keyboard)
        return

    # ===== Выбор сети для добавления кошелька =====
    if user_id in user_state and user_state[user_id].get("step") == "add_network":
        if text not in ["TRC20", "ERC20"]:
            await update.message.reply_text("Выберите TRC20 или ERC20", reply_markup=network_keyboard)
            return
        user_state[user_id]["step"] = "add_address"
        user_state[user_id]["network"] = text
        await update.message.reply_text(f"Введите адрес кошелька для сети {text}:", reply_markup=back_keyboard)
        return

    # ===== Ввод адреса для добавления =====
    if user_id in user_state and user_state[user_id].get("step") == "add_address":
        network = user_state[user_id]["network"]
        address = text.strip()
        wallet = {"network": network.upper(), "address": address}
        added = add_wallet(wallet)
        user_state.pop(user_id, None)
        if added:
            await update.message.reply_text(
                f"Кошелек {address} добавлен для сети {network} ✅",
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text(
                f"Кошелек {address} уже существует!",
                reply_markup=main_keyboard
            )
        return

    # ===== Неизвестная команда =====
    await update.message.reply_text(
        "Не понимаю команду. Выберите кнопку из меню.",
        reply_markup=main_keyboard
    )

# ===== Фоновый мониторинг =====
async def monitor_wallets_job(context):
    wallets = load_wallets()
    for w in wallets:
        network = w["network"]
        address = w["address"]
        info = check_wallet(w)
        balance = info["balance"]
        key = f"{network}_{address}"
        prev = previous_balances.get(key, 0)
        if balance > prev:
            await context.bot.send_message(
                chat_id=CHAT_ID,
                text=f"💰 Кошелек {address} ({network}) получил пополнение!\nБаланс: {balance}"
            )
        previous_balances[key] = balance

# ===== Запуск бота =====
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущен 🚀")

    # ===== Фоновый мониторинг каждые 60 секунд через JobQueue =====
    job_queue = app.job_queue
    job_queue.run_repeating(monitor_wallets_job, interval=60, first=1)

    # ===== Запуск бота =====
    app.run_polling()