"""Multi-step Khmer conversation for filling in fuel reports.

Flow branches by operation:
- Stock In  (ចូល): fuel → in/out → amount → source → notes → confirm
- Stock Out (ចេញ): fuel → in/out → vehicle type → truck → amount → notes → confirm

After confirm, the accountant can:
- Add similar (same fuel + same op + same vehicle type) → jump to truck/amount
- Add new (full restart, fresh selections)
- Done (end conversation)
"""
from __future__ import annotations

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .. import i18n, sheets, storage

log = logging.getLogger(__name__)

# Conversation states
FUEL, OPERATION, VEHICLE_TYPE, TRUCK, AMOUNT, SOURCE, NOTES, CONFIRM, AFTER_SAVE = range(9)


def _kb(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t, callback_data=d) for t, d in row] for row in rows]
    )


def _cancel_row() -> list[tuple[str, str]]:
    return [(i18n.BTN_CANCEL, "rep:cancel")]


def _session_date(context: ContextTypes.DEFAULT_TYPE):
    """Date used for new entries — overridden by /datelog, else today."""
    override = context.chat_data.get("override_date") if context.chat_data else None
    return override or sheets.now_local().date()


# ---------- Entry points ----------

async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    if not storage.is_user(user.id):
        await update.message.reply_text(
            i18n.NOT_WHITELISTED.format(user_id=user.id), parse_mode="HTML"
        )
        return ConversationHandler.END
    return await _ask_fuel(update, context, via_callback=False)


async def report_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user = update.effective_user
    if not storage.is_user(user.id):
        await query.edit_message_text(
            i18n.NOT_WHITELISTED.format(user_id=user.id), parse_mode="HTML"
        )
        return ConversationHandler.END
    return await _ask_fuel(update, context, via_callback=True)


# ---------- Step prompts (callable from anywhere in the flow) ----------

async def _ask_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE, *, via_callback: bool) -> int:
    context.user_data.clear()
    kb = _kb([
        [(i18n.FUEL_DIESEL, f"rep:fuel:{i18n.FUEL_DIESEL}"),
         (i18n.FUEL_GASOLINE, f"rep:fuel:{i18n.FUEL_GASOLINE}")],
        _cancel_row(),
    ])
    if via_callback:
        await update.callback_query.edit_message_text(i18n.ASK_FUEL_TYPE, reply_markup=kb)
    else:
        await update.message.reply_text(i18n.ASK_FUEL_TYPE, reply_markup=kb)
    return FUEL


async def _ask_operation(message_or_query, *, via_callback: bool) -> int:
    kb = _kb([
        [(i18n.OP_IN, f"rep:op:{i18n.OP_IN}"), (i18n.OP_OUT, f"rep:op:{i18n.OP_OUT}")],
        _cancel_row(),
    ])
    if via_callback:
        await message_or_query.edit_message_text(i18n.ASK_OPERATION, reply_markup=kb)
    else:
        await message_or_query.reply_text(i18n.ASK_OPERATION, reply_markup=kb)
    return OPERATION


async def _ask_vehicle_type(message_or_query, *, via_callback: bool) -> int:
    types = storage.load_vehicle_types()
    rows = [[(t, f"rep:vt:{i}")] for i, t in enumerate(types)]
    rows.append(_cancel_row())
    kb = _kb(rows)
    if via_callback:
        await message_or_query.edit_message_text(i18n.ASK_VEHICLE_TYPE, reply_markup=kb)
    else:
        await message_or_query.reply_text(i18n.ASK_VEHICLE_TYPE, reply_markup=kb)
    return VEHICLE_TYPE


async def _ask_truck(message_or_query, *, via_callback: bool) -> int:
    trucks = storage.load_trucks()
    rows: list[list[tuple[str, str]]] = []
    pair: list[tuple[str, str]] = []
    for t in trucks:
        label = f"#{t['no']} — {t['plate']}"
        pair.append((label, f"rep:tr:{t['no']}"))
        if len(pair) == 2:
            rows.append(pair)
            pair = []
    if pair:
        rows.append(pair)
    rows.append(_cancel_row())
    kb = _kb(rows)
    if via_callback:
        await message_or_query.edit_message_text(i18n.ASK_TRUCK, reply_markup=kb)
    else:
        await message_or_query.reply_text(i18n.ASK_TRUCK, reply_markup=kb)
    return TRUCK


async def _ask_amount(message_or_query, *, via_callback: bool) -> int:
    if via_callback:
        await message_or_query.edit_message_text(i18n.ASK_AMOUNT)
    else:
        await message_or_query.reply_text(i18n.ASK_AMOUNT)
    return AMOUNT


# ---------- State handlers ----------

async def on_fuel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    fuel = q.data.split(":", 2)[2]
    context.user_data["fuel"] = fuel
    return await _ask_operation(q, via_callback=True)


async def on_operation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    op = q.data.split(":", 2)[2]
    context.user_data["operation"] = op
    if op == i18n.OP_OUT:
        return await _ask_vehicle_type(q, via_callback=True)
    # Stock In: skip vehicle/truck, ask amount directly
    return await _ask_amount(q, via_callback=True)


async def on_vehicle_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    idx = int(q.data.split(":", 2)[2])
    types = storage.load_vehicle_types()
    context.user_data["vehicle_type"] = types[idx]
    return await _ask_truck(q, via_callback=True)


async def on_truck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    truck_no = int(q.data.split(":", 2)[2])
    trucks = storage.load_trucks()
    truck = next((t for t in trucks if t["no"] == truck_no), None)
    if truck is None:
        await q.edit_message_text(i18n.SAVE_ERROR)
        return ConversationHandler.END
    context.user_data["truck_no"] = truck["no"]
    context.user_data["plate"] = truck["plate"]
    return await _ask_amount(q, via_callback=True)


async def on_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (update.message.text or "").strip().replace(",", ".")
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(i18n.INVALID_AMOUNT)
        return AMOUNT
    context.user_data["amount"] = amount

    if context.user_data.get("operation") == i18n.OP_IN:
        await update.message.reply_text(i18n.ASK_SOURCE)
        return SOURCE

    kb = _kb([[(i18n.BTN_SKIP, "rep:notes:skip")], _cancel_row()])
    await update.message.reply_text(i18n.ASK_NOTES, reply_markup=kb)
    return NOTES


async def on_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["source"] = (update.message.text or "").strip()
    kb = _kb([[(i18n.BTN_SKIP, "rep:notes:skip")], _cancel_row()])
    await update.message.reply_text(i18n.ASK_NOTES, reply_markup=kb)
    return NOTES


async def on_notes_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["notes"] = (update.message.text or "").strip()
    return await _show_summary(update, context, via_callback=False)


async def on_notes_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    context.user_data["notes"] = ""
    return await _show_summary(update, context, via_callback=True)


async def _show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, *, via_callback: bool) -> int:
    d = context.user_data
    when = _session_date(context)
    if d.get("operation") == i18n.OP_IN:
        summary = i18n.CONFIRM_SUMMARY_IN.format(
            date=when.isoformat(),
            fuel=d["fuel"],
            operation=d["operation"],
            source=d.get("source") or i18n.fmt_no_notes(),
            amount=d["amount"],
            notes=d["notes"] or i18n.fmt_no_notes(),
        )
    else:
        summary = i18n.CONFIRM_SUMMARY_OUT.format(
            date=when.isoformat(),
            fuel=d["fuel"],
            operation=d["operation"],
            vehicle_type=d["vehicle_type"],
            truck_no=d["truck_no"],
            plate=d["plate"],
            amount=d["amount"],
            notes=d["notes"] or i18n.fmt_no_notes(),
        )
    kb = _kb([[(i18n.BTN_CONFIRM, "rep:save"), (i18n.BTN_CANCEL, "rep:cancel")]])
    if via_callback:
        await update.callback_query.edit_message_text(summary, reply_markup=kb, parse_mode="HTML")
    else:
        await update.message.reply_text(summary, reply_markup=kb, parse_mode="HTML")
    return CONFIRM


async def on_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    user = update.effective_user
    d = context.user_data
    entry = sheets.Entry(
        fuel_type=d["fuel"],
        operation=d["operation"],
        amount=d["amount"],
        notes=d["notes"],
        date=_session_date(context),
        submitter_name=user.full_name or user.username or str(user.id),
        submitter_username=user.username or "",
        submitter_phone=storage.get_phone(user.id),
        vehicle_type=d.get("vehicle_type", ""),
        truck_no=d.get("truck_no", 0),
        plate=d.get("plate", ""),
        source=d.get("source", ""),
    )
    try:
        sheets.append_entry(entry)
    except Exception:
        log.exception("Failed to append entry")
        await q.edit_message_text(i18n.SAVE_ERROR)
        return ConversationHandler.END

    kb = _kb([[
        (i18n.BTN_ADD_SIMILAR, "rep:more:similar"),
        (i18n.BTN_ADD_NEW, "rep:more:new"),
        (i18n.BTN_DONE, "rep:more:done"),
    ]])
    await q.edit_message_text(i18n.ASK_ANOTHER, reply_markup=kb)
    return AFTER_SAVE


async def on_after_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    choice = q.data.split(":", 2)[2]

    if choice == "done":
        await q.edit_message_text(i18n.SAVED_DONE)
        context.user_data.clear()
        return ConversationHandler.END

    if choice == "new":
        return await _ask_fuel(update, context, via_callback=True)

    # "similar": carry over fuel + op + (if Stock Out) vehicle_type
    op = context.user_data.get("operation")
    keep = {"fuel", "operation"}
    if op == i18n.OP_OUT:
        keep.update({"vehicle_type"})
    for k in list(context.user_data.keys()):
        if k not in keep:
            context.user_data.pop(k, None)

    if op == i18n.OP_OUT:
        return await _ask_truck(q, via_callback=True)
    # Stock In
    return await _ask_amount(q, via_callback=True)


async def on_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(i18n.CANCELED)
    else:
        await update.message.reply_text(i18n.CANCELED)
    context.user_data.clear()
    return ConversationHandler.END


def build_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            CommandHandler("report", report_cmd),
            CallbackQueryHandler(report_button, pattern=r"^report:start$"),
        ],
        states={
            FUEL: [CallbackQueryHandler(on_fuel, pattern=r"^rep:fuel:")],
            OPERATION: [CallbackQueryHandler(on_operation, pattern=r"^rep:op:")],
            VEHICLE_TYPE: [CallbackQueryHandler(on_vehicle_type, pattern=r"^rep:vt:")],
            TRUCK: [CallbackQueryHandler(on_truck, pattern=r"^rep:tr:")],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_amount)],
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, on_source)],
            NOTES: [
                CallbackQueryHandler(on_notes_skip, pattern=r"^rep:notes:skip$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_notes_text),
            ],
            CONFIRM: [
                CallbackQueryHandler(on_save, pattern=r"^rep:save$"),
                CallbackQueryHandler(on_cancel, pattern=r"^rep:cancel$"),
            ],
            AFTER_SAVE: [
                CallbackQueryHandler(on_after_save, pattern=r"^rep:more:"),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", on_cancel),
            CallbackQueryHandler(on_cancel, pattern=r"^rep:cancel$"),
        ],
        allow_reentry=True,
    )
