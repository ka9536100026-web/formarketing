import logging
import os
import random

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from .texts import (
    START_MESSAGE,
    HELP_MESSAGE,
    AUTHORS,
    QUOTES,
    build_authors_keyboard,
    build_quote_text,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    keyboard = build_authors_keyboard()
    await update.message.reply_text(
        START_MESSAGE,
        reply_markup=keyboard,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    keyboard = build_authors_keyboard()
    await update.message.reply_text(
        HELP_MESSAGE,
        reply_markup=keyboard,
    )


async def handle_author_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка нажатия на кнопку с выбором авторки."""
    query = update.callback_query
    await query.answer()

    author_key = query.data

    if author_key not in AUTHORS:
        await query.edit_message_text(
            text="Кажется, что-то пошло не так. Попробуйте выбрать авторку ещё раз.",
            reply_markup=build_authors_keyboard(),
        )
        return

    full_name = AUTHORS[author_key]
    quotes_for_author = QUOTES.get(author_key, [])

    if not quotes_for_author:
        text = f"К сожалению, цитаты для {full_name} временно недоступны."
    else:
        quote = random.choice(quotes_for_author)
        text = build_quote_text(full_name, quote)

    await query.edit_message_text(
        text=text,
        reply_markup=build_authors_keyboard(),
    )


def get_webhook_base_url() -> str:
    """Определяем базовый URL для вебхука.

    На Render.com можно использовать переменную окружения RENDER_EXTERNAL_URL.
    При локальной разработке можно задать WEBHOOK_BASE_URL вручную.
    """
    base_url = os.getenv("WEBHOOK_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL")
    if not base_url:
        logger.warning(
            "WEBHOOK_BASE_URL и RENDER_EXTERNAL_URL не заданы. " 
            "Для работы вебхуков в продакшене нужно указать один из этих параметров."
        )
        # Для локальной разработки можно вернуть фиктивный URL или выбросить ошибку.
        # Здесь вернем пустую строку, чтобы run_webhook не пытался зарегистрировать вебхук.
    return base_url


def main() -> None:
    """Точка входа в приложение.

    Здесь создаётся и запускается Telegram-бот в режиме вебхуков.
    """
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Не задана переменная окружения BOT_TOKEN с токеном бота.")

    application = Application.builder().token(token).build()

    # Регистрируем обработчики команд и колбэков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(handle_author_choice))

    port = int(os.getenv("PORT", "10000"))

    webhook_base_url = get_webhook_base_url()

    if webhook_base_url:
        # Запуск в режиме вебхуков (Render.com)
        webhook_path = "telegram-webhook"
        webhook_url = f"{webhook_base_url.rstrip('/')}/{webhook_path}"
        logger.info("Запускаем бота в режиме вебхуков. Webhook URL: %s", webhook_url)

        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=webhook_path,
            webhook_url=webhook_url,
        )
    else:
        # Fallback-режим: можно использовать локально с polling,
        # но на Render.com рекомендуется настроить именно вебхуки.
        logger.warning(
            "WEBHOOK_BASE_URL не указан. Бот будет запущен в режиме polling. " 
            "В продакшене на Render.com обязательно настройте WEBHOOK_BASE_URL или RENDER_EXTERNAL_URL."
        )
        application.run_polling()


if __name__ == "__main__":
    main()
