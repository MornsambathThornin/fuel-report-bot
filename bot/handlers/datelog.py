"""/datelog — let the accountant backdate session entries to a specific date."""
from __future__ import annotations

import datetime as dt

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from .. import i18n, sheets, storage


async def datelog_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not storage.is_user(user.id):
        await update.message.reply_text(
            i18n.NOT_WHITELISTED.format(user_id=user.id), parse_mode="HTML"
        )
        return

    args = context.args
    if not args:
        current = context.chat_data.get("override_date") or sheets.now_local().date()
        await update.message.reply_text(
            i18n.DATELOG_CURRENT.format(date=current.isoformat())
        )
        return

    arg = args[0].strip().lower()
    if arg in ("reset", "today", "clear"):
        context.chat_data.pop("override_date", None)
        await update.message.reply_text(i18n.DATELOG_RESET)
        return
    if arg == "show":
        current = context.chat_data.get("override_date") or sheets.now_local().date()
        await update.message.reply_text(
            i18n.DATELOG_CURRENT.format(date=current.isoformat())
        )
        return

    try:
        d = dt.date.fromisoformat(args[0].strip())
    except ValueError:
        await update.message.reply_text(i18n.DATELOG_INVALID)
        return

    context.chat_data["override_date"] = d
    await update.message.reply_text(i18n.DATELOG_SET.format(date=d.isoformat()))


def register(app) -> None:
    app.add_handler(CommandHandler("datelog", datelog_cmd))
