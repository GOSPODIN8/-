import os, logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, MessageHandler, filters, ContextTypes
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# ── Токен берётся из переменной окружения (Railway ставит автоматически) ──
BOT_TOKEN  = os.environ.get("BOT_TOKEN", "")
PRICE_RU   = 50
PRICE_TG   = 50
PRICE_BOTH = 80
FILE_RU    = "33_istiny_ru.pdf"
FILE_TG    = "33_hakikat_tg.pdf"

PAYLOAD_RU   = "book_ru"
PAYLOAD_TG   = "book_tg"
PAYLOAD_BOTH = "book_both"
PRODUCT_MAP  = {PAYLOAD_RU: ("ru",), PAYLOAD_TG: ("tg",), PAYLOAD_BOTH: ("ru","tg")}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "друг"
    text = (
        f"👋 Привет, *{name}*!\n\n"
        "Добро пожаловать в магазин книги\n"
        "📖 *«33 жёсткие истины, которые изменят твою жизнь»*\n\n"
        "✍️ Автор: *Эдриан Трейп*\n\n"
        "Психология отношений · Бизнес · Мотивация\n\n"
        "Каждая глава содержит:\n"
        "• Жёсткую истину\n"
        "• Объяснение\n"
        "• Реальный пример из жизни\n"
        "• Конкретное действие\n\n"
        "👇 Выбери версию:"
    )
    kb = [
        [InlineKeyboardButton(f"🇷🇺 Русская версия — {PRICE_RU} ⭐️", callback_data="buy_ru")],
        [InlineKeyboardButton(f"🇹🇯 Таджикская версия — {PRICE_TG} ⭐️", callback_data="buy_tg")],
        [InlineKeyboardButton(f"📦 Обе версии — {PRICE_BOTH} ⭐️ (выгодно!)", callback_data="buy_both")],
        [InlineKeyboardButton("ℹ️ Что внутри?", callback_data="about")],
    ]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    text = (
        "📖 *О книге «33 жёсткие истины»*\n\n"
        "❤️ *Часть 1 — Отношения (1–11)*\n"
        "Тебя любят так, как ты позволяешь. Молчание — тоже ответ. "
        "Семья — не оправдание токсичности. Прощение — для тебя.\n\n"
        "💼 *Часть 2 — Бизнес (12–22)*\n"
        "Идея без действия — мечта. Деньги как энергия. "
        "Провал — это данные. Клиент платит за трансформацию.\n\n"
        "🔥 *Часть 3 — Мотивация (23–33)*\n"
        "Дисциплина важнее мотивации. Окружение = судьба. "
        "Твоя жизнь — твоя ответственность.\n\n"
        "💡 33 главы · Живые примеры · Действие в каждой главе\n\n"
        "✍️ *Эдриан Трейп*"
    )
    kb = [
        [InlineKeyboardButton(f"🇷🇺 Купить русскую — {PRICE_RU} ⭐️", callback_data="buy_ru")],
        [InlineKeyboardButton(f"🇹🇯 Купить таджикскую — {PRICE_TG} ⭐️", callback_data="buy_tg")],
        [InlineKeyboardButton(f"📦 Купить обе — {PRICE_BOTH} ⭐️", callback_data="buy_both")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back")],
    ]
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))


async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    kb = [
        [InlineKeyboardButton(f"🇷🇺 Русская версия — {PRICE_RU} ⭐️", callback_data="buy_ru")],
        [InlineKeyboardButton(f"🇹🇯 Таджикская версия — {PRICE_TG} ⭐️", callback_data="buy_tg")],
        [InlineKeyboardButton(f"📦 Обе версии — {PRICE_BOTH} ⭐️ (выгодно!)", callback_data="buy_both")],
        [InlineKeyboardButton("ℹ️ Что внутри?", callback_data="about")],
    ]
    await q.edit_message_text("👇 Выбери версию книги:", reply_markup=InlineKeyboardMarkup(kb))


async def send_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "buy_ru":
        title, desc, payload, price = (
            "📖 «33 жёсткие истины» — Русская версия",
            "PDF-книга на русском. 33 главы о психологии, бизнесе и мотивации. Автор: Эдриан Трейп.",
            PAYLOAD_RU, PRICE_RU
        )
    elif q.data == "buy_tg":
        title, desc, payload, price = (
            "📖 «33 хакикати сахт» — Версияи точики",
            "Китоби PDF ба точики. 33 боб. Муаллиф: Эдриан Трейп.",
            PAYLOAD_TG, PRICE_TG
        )
    else:
        title, desc, payload, price = (
            "📦 «33 жёсткие истины» — Обе версии",
            "Русская + таджикская PDF-книги. 33 главы. Автор: Эдриан Трейп.",
            PAYLOAD_BOTH, PRICE_BOTH
        )
    await context.bot.send_invoice(
        chat_id=q.message.chat_id, title=title, description=desc,
        payload=payload, currency="XTR",
        prices=[LabeledPrice("Оплата", price)], provider_token=""
    )


async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload  = update.message.successful_payment.invoice_payload
    name     = update.effective_user.first_name or "друг"
    chat_id  = update.effective_chat.id
    variants = PRODUCT_MAP.get(payload, ())

    await update.message.reply_text(
        f"🎉 *Спасибо за покупку, {name}!*\n\nОтправляю книгу прямо сейчас... ✈️",
        parse_mode="Markdown"
    )

    for v in variants:
        fname = FILE_RU if v == "ru" else FILE_TG
        cap_ru = (
            "📖 *«33 жёсткие истины, которые изменят твою жизнь»*\n\n"
            "Читай медленно — каждая истина заслуживает честного разговора с собой.\n\n"
            "✍️ *Эдриан Трейп*"
        )
        cap_tg = (
            "📖 *«33 хакикати сахте, ки зиндагии туро тагйир медиханд»*\n\n"
            "Охиста бихон — хар хакикат сазовори гуфтугуи самимии бо худат аст.\n\n"
            "✍️ *Эдриан Трейп*"
        )
        caption = cap_ru if v == "ru" else cap_tg
        fn_out  = "33_Zhestkie_Istiny.pdf" if v == "ru" else "33_Hakikat.pdf"
        try:
            with open(fname, "rb") as f:
                await context.bot.send_document(
                    chat_id=chat_id, document=f,
                    filename=fn_out, caption=caption, parse_mode="Markdown", protect\_content=True
                )
        except FileNotFoundError:
            await context.bot.send_message(chat_id=chat_id,
                text="⚠️ Файл временно недоступен. Напишите нам — отправим вручную.")

    await update.message.reply_text(
        "💡 Читай по одной истине в день.\n33 дня — и жизнь начнёт меняться.\n\nПонравилось? Поделись с другом 🙏",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 /start — главное меню\n\nОплата через Telegram Stars ⭐️\nКнига приходит автоматически."
    )


def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не задан! Добавь его в переменные окружения Railway.")
        return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  help_cmd))
    app.add_handler(CallbackQueryHandler(about,        pattern="^about$"))
    app.add_handler(CallbackQueryHandler(back,         pattern="^back$"))
    app.add_handler(CallbackQueryHandler(send_invoice, pattern="^buy_"))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    print("✅ Бот запущен!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
