import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from db import add_wallet
from utils import detect_chain
from chains.tron import get_trc20_usdt
from chains.ethereum import get_erc20_usdt
from chains.bsc import get_bep20_usdt
from analytics import summarize
from scheduler import start_scheduler

TOKEN = os.getenv("TOKEN")
ETH_API = os.getenv("ETH_API")
BSC_API = os.getenv("BSC_API")


# ================= МЕНЮ =================
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🔎 Проверить кошелек", callback_data="check")],
        [InlineKeyboardButton("📡 Мониторинг кошельков", callback_data="monitor")],
        [InlineKeyboardButton("ℹ FAQ", callback_data="faq")]
    ]
    return InlineKeyboardMarkup(keyboard)


def network_menu():
    keyboard = [
        [InlineKeyboardButton("TRC20", callback_data="trc20")],
        [InlineKeyboardButton("ERC20", callback_data="erc20")],
        [InlineKeyboardButton("BEP20", callback_data="bep20")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    return InlineKeyboardMarkup(keyboard)


# ================= ОБРАБОТЧИКИ =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Главное меню", reply_markup=main_menu())


# FAQ
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "чекер нужен для проверки кошельков,\n"
        "вы можете проверять кошельки сетей trc20, bep20, erc20"
    )
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# Проверка кошелька
async def check_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Выберите сеть:", reply_markup=network_menu())


async def choose_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["network"] = query.data
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
    await query.edit_message_text(
        f"Введите адрес для сети {query.data.upper()}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "network" not in context.user_data:
        return

    address = update.message.text.strip()
    network = context.user_data["network"]
    txs = []

    try:
        if network == "trc20":
            txs = get_trc20_usdt(address)
        elif network == "erc20":
            txs = get_erc20_usdt(address, ETH_API)
        elif network == "bep20":
            txs = get_bep20_usdt(address, BSC_API)

        stats = summarize(txs)
        text = f"📊 Анализ {network.upper()}\nТранзакций: {stats['count']}\nОбъем: {stats['total']} USDT"

    except Exception as e:
        text = f"Ошибка при проверке: {e}"

    await update.message.reply_text(text, reply_markup=main_menu())
    context.user_data.clear()


# Мониторинг
async def monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    await query.edit_message_text("Мониторинг кошельков:", reply_markup=InlineKeyboardMarkup(keyboard))


async def add_wallet_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adding"] = True
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back")]]
    await query.edit_message_text(
        "Введите адрес и сеть через пробел\nПример: 0x123...
        ERC20",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("adding"):
        return
    try:
        address, network = update.message.text.split()
        add_wallet(update.effective_user.id, address, network)
        await update.message.reply_text("Кошелек добавлен ✅", reply_markup=main_menu())
        context.user_data.clear()
    except:
        await update.message.reply_text("Неверный формат. Пример: 0x123... ERC20")


# Кнопка назад
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📌 Главное меню", reply_markup=main_menu())


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))

    # CallbackQuery
    app.add_handler(CallbackQueryHandler(faq, pattern="faq"))
    app.add_handler(CallbackQueryHandler(check_wallet, pattern="check"))
    app.add_handler(CallbackQueryHandler(choose_network, pattern="trc20|erc20|bep20"))
    app.add_handler(CallbackQueryHandler(monitoring, pattern="monitor"))
    app.add_handler(CallbackQueryHandler(add_wallet_prompt, pattern="add_wallet"))
    app.add_handler(CallbackQueryHandler(back, pattern="back"))

    # Обработка текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_wallet))

    # Авто-проверка
    start_scheduler(app)

    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()