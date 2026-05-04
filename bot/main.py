"""Telegram bot entry point."""
import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from . import config, storage
from .handlers import admin as admin_handlers
from .handlers import datelog as datelog_handlers
from .handlers import report as report_handlers
from .handlers.start import help_cmd, on_contact, start

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def build_app() -> Application:
    config.assert_ready()
    storage.ensure_data_files()
    storage.bootstrap_admin_if_empty()
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.CONTACT, on_contact))
    datelog_handlers.register(app)
    app.add_handler(report_handlers.build_conversation())
    admin_handlers.register(app)
    return app


def main() -> None:
    app = build_app()
    app.run_polling()


if __name__ == "__main__":
    main()
