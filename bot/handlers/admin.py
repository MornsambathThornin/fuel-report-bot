"""Admin commands for managing whitelist, trucks, vehicle types, and beginning balance."""
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from .. import i18n, sheets, storage


def _admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not storage.is_admin(update.effective_user.id):
            await update.message.reply_text(i18n.ADMIN_ONLY)
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


def _parse_id_and_name(args: list[str]) -> tuple[int, str] | None:
    if len(args) < 2:
        return None
    try:
        uid = int(args[0])
    except ValueError:
        return None
    name = " ".join(args[1:]).strip()
    if not name:
        return None
    return uid, name


@_admin_only
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parsed = _parse_id_and_name(context.args)
    if parsed is None:
        await update.message.reply_text(i18n.USAGE_ADDUSER)
        return
    uid, name = parsed
    storage.add_user(uid, name, as_admin=False)
    await update.message.reply_text(i18n.USER_ADDED.format(name=name, user_id=uid))


@_admin_only
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    parsed = _parse_id_and_name(context.args)
    if parsed is None:
        await update.message.reply_text(i18n.USAGE_ADDADMIN)
        return
    uid, name = parsed
    storage.add_user(uid, name, as_admin=True)
    await update.message.reply_text(i18n.ADMIN_ADDED.format(name=name, user_id=uid))


@_admin_only
async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text(i18n.USAGE_REMOVEADMIN)
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text(i18n.USAGE_REMOVEADMIN)
        return
    try:
        if not storage.demote_admin(uid):
            await update.message.reply_text(i18n.ADMIN_NOT_FOUND.format(user_id=uid))
            return
    except storage.LastAdminError:
        await update.message.reply_text(i18n.LAST_ADMIN_ERROR)
        return
    await update.message.reply_text(i18n.ADMIN_DEMOTED.format(user_id=uid))


@_admin_only
async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text(i18n.USAGE_REMOVEUSER)
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text(i18n.USAGE_REMOVEUSER)
        return
    if storage.remove_user(uid):
        await update.message.reply_text(i18n.USER_REMOVED.format(user_id=uid))
    else:
        await update.message.reply_text(i18n.USER_NOT_FOUND.format(user_id=uid))


@_admin_only
async def listusers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    wl = storage.load_whitelist()
    out = i18n.LIST_USERS_TITLE
    if wl["users"]:
        for u in wl["users"]:
            out += f"  • {u['name']} — <code>{u['id']}</code>\n"
    else:
        out += i18n.LIST_EMPTY + "\n"
    out += i18n.LIST_ADMINS_TITLE
    if wl["admins"]:
        for a in wl["admins"]:
            out += f"  • {a['name']} — <code>{a['id']}</code>\n"
    else:
        out += i18n.LIST_EMPTY + "\n"
    await update.message.reply_text(out, parse_mode="HTML")


@_admin_only
async def listtrucks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    trucks = storage.load_trucks()
    out = i18n.LIST_TRUCKS_TITLE.format(count=len(trucks))
    if trucks:
        for t in trucks:
            out += f"  • #{t['no']} — <code>{t['plate']}</code>\n"
    else:
        out += i18n.LIST_EMPTY + "\n"
    await update.message.reply_text(out, parse_mode="HTML")


@_admin_only
async def listvehicletypes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    types = storage.load_vehicle_types()
    out = i18n.LIST_VEHTYPES_TITLE.format(count=len(types))
    if types:
        for t in types:
            out += f"  • {t}\n"
    else:
        out += i18n.LIST_EMPTY + "\n"
    await update.message.reply_text(out, parse_mode="HTML")


@_admin_only
async def addtruck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text(i18n.USAGE_ADDTRUCK)
        return
    plate = context.args[0].strip()
    storage.add_truck(plate)
    await update.message.reply_text(i18n.TRUCK_ADDED.format(plate=plate))


@_admin_only
async def removetruck(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text(i18n.USAGE_REMOVETRUCK)
        return
    plate = context.args[0].strip()
    if storage.remove_truck(plate):
        await update.message.reply_text(i18n.TRUCK_REMOVED.format(plate=plate))
    else:
        await update.message.reply_text(i18n.TRUCK_NOT_FOUND.format(plate=plate))


@_admin_only
async def addvehicletype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(i18n.USAGE_ADDVEHTYPE)
        return
    name = " ".join(context.args).strip()
    storage.add_vehicle_type(name)
    await update.message.reply_text(i18n.VEHTYPE_ADDED.format(name=name))


@_admin_only
async def removevehicletype(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text(i18n.USAGE_REMOVEVEHTYPE)
        return
    name = " ".join(context.args).strip()
    if storage.remove_vehicle_type(name):
        await update.message.reply_text(i18n.VEHTYPE_REMOVED.format(name=name))
    else:
        await update.message.reply_text(i18n.VEHTYPE_NOT_FOUND.format(name=name))


@_admin_only
async def setbeginning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text(i18n.USAGE_SETBEGIN)
        return
    fuel = context.args[0].strip()
    if fuel not in (i18n.FUEL_DIESEL, i18n.FUEL_GASOLINE):
        await update.message.reply_text(i18n.INVALID_FUEL)
        return
    try:
        amount = float(context.args[1].replace(",", "."))
    except ValueError:
        await update.message.reply_text(i18n.INVALID_NUMBER)
        return
    tab = sheets.set_beginning_balance(fuel, amount)
    await update.message.reply_text(
        i18n.BEGINNING_SET.format(fuel=fuel, amount=amount, month=tab)
    )


@_admin_only
async def setphone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text(i18n.USAGE_SETPHONE)
        return
    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text(i18n.USAGE_SETPHONE)
        return
    phone = context.args[1].strip()
    if not phone.startswith("+"):
        phone = "+" + phone
    if not storage.set_phone(uid, phone):
        await update.message.reply_text(i18n.USER_NOT_FOUND.format(user_id=uid))
        return
    await update.message.reply_text(i18n.PHONE_SET.format(phone=phone, user_id=uid))


@_admin_only
async def sheet_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(i18n.SHEET_LINK.format(url=sheets.sheet_url()))


def register(app) -> None:
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("listusers", listusers))
    app.add_handler(CommandHandler("addtruck", addtruck))
    app.add_handler(CommandHandler("removetruck", removetruck))
    app.add_handler(CommandHandler("listtrucks", listtrucks))
    app.add_handler(CommandHandler("addvehicletype", addvehicletype))
    app.add_handler(CommandHandler("removevehicletype", removevehicletype))
    app.add_handler(CommandHandler("listvehicletypes", listvehicletypes))
    app.add_handler(CommandHandler("setbeginning", setbeginning))
    app.add_handler(CommandHandler("setphone", setphone))
    app.add_handler(CommandHandler("sheet", sheet_link))
