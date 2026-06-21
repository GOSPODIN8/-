import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice,
    PreCheckoutQuery,
    FSInputFile,
)
from aiogram.filters import CommandStart

# ----------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------
# Token comes from an environment variable (set this in Railway, not in code).
BOT_TOKEN = os.environ["BOT_TOKEN"]

PRICE_STARS = 288  # price in Telegram Stars for EACH version

PRODUCTS = {
    "ru": {
        "title": "8 важных законов денег (RU)",
        "description": (
            "Книга «8 важных законов денег». Автор: Эдриан Трейп. "
            "Русская версия, PDF."
        ),
        "file_path": "files/8_zakonov_deneg_RU.pdf",
        "file_name": "8_zakonov_deneg_RU.pdf",
    },
    "tg": {
        "title": "8 қонуни муҳими пул (TG)",
        "description": (
            "Китоби «8 қонуни муҳими пул». Муаллиф: Эдриан Трейп. "
            "Нусхаи тоҷикӣ, PDF."
        ),
        "file_path": "files/8_qonuni_pul_TG.pdf",
        "file_name": "8_qonuni_pul_TG.pdf",
    },
}

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ----------------------------------------------------------------------
# /start — show the shop menu
# ----------------------------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"🇷🇺 Русская версия — {PRICE_STARS} ⭐",
                callback_data="buy_ru",
            )],
            [InlineKeyboardButton(
                text=f"🇹🇯 Тоҳикӣ версия — {PRICE_STARS} ⭐",
                callback_data="buy_tg",
            )],
        ]
    )
    await message.answer(
        "📖 <b>«8 важных законов денег»</b>\n"
        "Автор: Эдриан Трейп\n\n"
        "Восемь простых, проверяемых законов о том, как зарабатывать, "
        "сохранять и приумножать деньги.\n\n"
        "Выберите версию книги, которую хотите приобрести:",
        reply_markup=kb,
        parse_mode="HTML",
    )


# ----------------------------------------------------------------------
# Buy button -> send invoice (Telegram Stars)
# ----------------------------------------------------------------------
@dp.callback_query(F.data.in_({"buy_ru", "buy_tg"}))
async def on_buy(callback: CallbackQuery):
    lang = "ru" if callback.data == "buy_ru" else "tg"
    product = PRODUCTS[lang]

    await callback.message.answer_invoice(
        title=product["title"],
        description=product["description"],
        payload=f"book_{lang}",        # we read this back after payment
        currency="XTR",                # XTR = Telegram Stars
        prices=[LabeledPrice(label=product["title"], amount=PRICE_STARS)],
        # NOTE: for XTR, amount is the number of Stars directly (no cents).
    )
    await callback.answer()


# ----------------------------------------------------------------------
# Telegram asks us to confirm the order before charging the user
# ----------------------------------------------------------------------
@dp.pre_checkout_query()
async def on_pre_checkout(pre_checkout_q: PreCheckoutQuery):
    # Always approve here unless you have a reason to reject
    # (e.g. item no longer available).
    await pre_checkout_q.answer(ok=True)


# ----------------------------------------------------------------------
# Payment succeeded -> deliver the PDF
# ----------------------------------------------------------------------
@dp.message(F.successful_payment)
async def on_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload  # "book_ru" / "book_tg"
    lang = payload.replace("book_", "")
    product = PRODUCTS.get(lang)

    if not product:
        await message.answer(
            "Оплата получена, но возникла ошибка при определении товара. "
            "Напишите, пожалуйста, в поддержку."
        )
        return

    await message.answer("✅ Оплата получена! Отправляю книгу…")
    file = FSInputFile(product["file_path"], filename=product["file_name"])
    await message.answer_document(file, caption=f"📖 {product['title']}\nСпасибо за покупку!")


# ----------------------------------------------------------------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
