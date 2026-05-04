"""/start, /help, whitelist guard, and contact-share flow."""
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes

from .. import i18n, storage


def _menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(i18n.BTN_REPORT, callback_data="report:start")]]
    )


def _contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(i18n.BTN_SHARE_CONTACT, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not storage.is_user(user.id):
        await update.message.reply_text(
            i18n.NOT_WHITELISTED.format(user_id=user.id),
            parse_mode="HTML",
        )
        return

    name = user.first_name or user.username or str(user.id)

    if not storage.get_phone(user.id):
        await update.message.reply_text(
            i18n.WELCOME.format(name=name),
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            i18n.ASK_CONTACT,
            reply_markup=_contact_keyboard(),
        )
        return

    await update.message.reply_text(
        i18n.WELCOME.format(name=name),
        reply_markup=_menu_keyboard(),
    )


async def on_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not storage.is_user(user.id):
        await update.message.reply_text(
            i18n.NOT_WHITELISTED.format(user_id=user.id), parse_mode="HTML"
        )
        return

    contact = update.message.contact
    if contact.user_id and contact.user_id != user.id:
        await update.message.reply_text(i18n.CONTACT_NOT_OWN)
        return

    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    storage.set_phone(user.id, phone)

    await update.message.reply_text(
        i18n.CONTACT_SAVED.format(phone=phone),
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        i18n.WELCOME.format(name=user.first_name or user.username or str(user.id)),
        reply_markup=_menu_keyboard(),
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not storage.is_user(user.id):
        await update.message.reply_text(
            i18n.NOT_WHITELISTED.format(user_id=user.id),
            parse_mode="HTML",
        )
        return
    text = i18n.HELP_USER
    if storage.is_admin(user.id):
        text += i18n.HELP_ADMIN
    await update.message.reply_text(text, parse_mode="HTML")
