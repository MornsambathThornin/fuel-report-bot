"""All Khmer-language strings shown to users. Edit here to change wording."""

FUEL_DIESEL = "ម៉ាស៊ូត"
FUEL_GASOLINE = "ប្រេងសំាង"

OP_IN = "ចូល"
OP_OUT = "ចេញ"

BTN_REPORT = "📝 បំពេញរបាយការណ៍"
BTN_CANCEL = "❌ បោះបង់"
BTN_CONFIRM = "✅ បញ្ជាក់"
BTN_SKIP = "⏭ រំលង"
BTN_SHARE_CONTACT = "📞 ចែករំលែកលេខទូរស័ព្ទ"

ASK_CONTACT = (
    "សូមចែករំលែកលេខទូរស័ព្ទរបស់អ្នកដោយចុចប៊ូតុងខាងក្រោម។\n"
    "(ត្រូវធ្វើតែម្តងគត់)"
)
CONTACT_SAVED = "✅ បានរក្សាទុកលេខទូរស័ព្ទ {phone}"
CONTACT_NOT_OWN = "⚠️ សូមចែករំលែកលេខទូរស័ព្ទ​របស់​អ្នក​ផ្ទាល់ មិនមែនរបស់អ្នកដទៃទេ។"

WELCOME = (
    "សួស្តី {name}!\n"
    "ស្វាគមន៍មកកាន់ប្រព័ន្ធកត់ត្រាការប្រើប្រាស់ប្រេងឥន្ធនៈ។\n\n"
    "សូមចុចប៊ូតុងខាងក្រោមដើម្បីបំពេញរបាយការណ៍។"
)

NOT_WHITELISTED = (
    "សុំទោស អ្នកមិនមានសិទ្ធិប្រើប្រាស់ bot នេះទេ។\n"
    "សូមទាក់ទងអ្នកគ្រប់គ្រងដើម្បីបន្ថែមអ្នកក្នុងបញ្ជី។\n\n"
    "Telegram ID របស់អ្នក៖ <code>{user_id}</code>"
)

ASK_FUEL_TYPE = "សូមជ្រើសរើសប្រភេទប្រេងឥន្ធនៈ៖"
ASK_OPERATION = "សូមជ្រើសរើសប្រភេទប្រតិបត្តិការ៖"
ASK_VEHICLE_TYPE = "សូមជ្រើសរើសប្រភេទយានយន្ត៖"
ASK_TRUCK = "សូមជ្រើសរើសឡាន៖"
ASK_AMOUNT = "សូមបញ្ចូលបរិមាណ (លីត្រ)៖"
ASK_SOURCE = "សូមបញ្ចូលប្រភព (ឈ្មោះក្រុមហ៊ុនទូទាត់)៖"
ASK_NOTES = "សូមបញ្ចូលផ្សេងៗ (ឬចុច «រំលង» ប្រសិនបើគ្មាន)៖"

INVALID_AMOUNT = "បរិមាណមិនត្រឹមត្រូវ។ សូមបញ្ចូលលេខ (ឧ. 50 ឬ 25.5)។"

CONFIRM_SUMMARY_OUT = (
    "<b>សូមពិនិត្យឡើងវិញ៖</b>\n\n"
    "📅 ថ្ងៃ៖ {date}\n"
    "⛽ ប្រេង៖ {fuel}\n"
    "🔄 ប្រតិបត្តិការ៖ {operation}\n"
    "🚛 យានយន្ត៖ {vehicle_type} #{truck_no} ({plate})\n"
    "💧 បរិមាណ៖ {amount} លីត្រ\n"
    "📝 ផ្សេងៗ៖ {notes}\n\n"
    "តើព័ត៌មានត្រឹមត្រូវទេ?"
)

CONFIRM_SUMMARY_IN = (
    "<b>សូមពិនិត្យឡើងវិញ៖</b>\n\n"
    "📅 ថ្ងៃ៖ {date}\n"
    "⛽ ប្រេង៖ {fuel}\n"
    "🔄 ប្រតិបត្តិការ៖ {operation}\n"
    "🏢 ប្រភព៖ {source}\n"
    "💧 បរិមាណ៖ {amount} លីត្រ\n"
    "📝 ផ្សេងៗ៖ {notes}\n\n"
    "តើព័ត៌មានត្រឹមត្រូវទេ?"
)

ASK_ANOTHER = "✅ បានរក្សាទុក! តើបន្ថែមរបាយការណ៍ទៀតទេ?"
BTN_ADD_SIMILAR = "➕ ដូចគ្នា"
BTN_ADD_NEW = "🔄 ថ្មី"
BTN_DONE = "🏁 បញ្ចប់"

SAVED_DONE = "✅ បានបញ្ចប់។ សូមអរគុណ!"
CANCELED = "❌ បានបោះបង់។"
SAVE_ERROR = "⚠️ មានបញ្ហាក្នុងការរក្សាទុក។ សូមព្យាយាមម្តងទៀត ឬទាក់ទងអ្នកគ្រប់គ្រង។"

# /datelog
DATELOG_SET = "✅ កំណត់ថ្ងៃសម្រាប់របាយការណ៍ថ្មីៗទាំងអស់ជា {date}"
DATELOG_RESET = "✅ បានត្រឡប់ទៅប្រើថ្ងៃបច្ចុប្បន្ន"
DATELOG_CURRENT = "ថ្ងៃដែលកំពុងប្រើ៖ {date}"
DATELOG_INVALID = "⚠️ ទម្រង់ថ្ងៃមិនត្រឹមត្រូវ។ ប្រើ YYYY-MM-DD (ឧ. 2026-04-26)"

# Admin
ADMIN_ONLY = "⛔ ពាក្យបញ្ជានេះសម្រាប់តែអ្នកគ្រប់គ្រងប៉ុណ្ណោះ។"
USAGE_ADDUSER = "ប្រើប្រាស់៖ /adduser <telegram_id> <ឈ្មោះ>"
USAGE_REMOVEUSER = "ប្រើប្រាស់៖ /removeuser <telegram_id>"
USAGE_ADDADMIN = "ប្រើប្រាស់៖ /addadmin <telegram_id> <ឈ្មោះ>"
USAGE_REMOVEADMIN = "ប្រើប្រាស់៖ /removeadmin <telegram_id>"
USAGE_ADDTRUCK = "ប្រើប្រាស់៖ /addtruck <ផ្លាកលេខ>"
USAGE_REMOVETRUCK = "ប្រើប្រាស់៖ /removetruck <ផ្លាកលេខ>"
USAGE_ADDVEHTYPE = "ប្រើប្រាស់៖ /addvehicletype <ឈ្មោះ>"
USAGE_REMOVEVEHTYPE = "ប្រើប្រាស់៖ /removevehicletype <ឈ្មោះ>"
USAGE_SETBEGIN = "ប្រើប្រាស់៖ /setbeginning <ម៉ាស៊ូត|ប្រេងសំាង> <ចំនួន>"
USAGE_SETPHONE = "ប្រើប្រាស់៖ /setphone <telegram_id> <លេខទូរស័ព្ទ>"
PHONE_SET = "✅ បានកំណត់លេខទូរស័ព្ទ {phone} សម្រាប់អ្នកប្រើ {user_id}"

USER_ADDED = "✅ បានបន្ថែមអ្នកប្រើប្រាស់ {name} ({user_id})"
USER_REMOVED = "✅ បានដកអ្នកប្រើប្រាស់ {user_id}"
USER_NOT_FOUND = "⚠️ រកមិនឃើញអ្នកប្រើប្រាស់ {user_id}"
ADMIN_ADDED = "✅ បានបន្ថែមអ្នកគ្រប់គ្រង {name} ({user_id})"
ADMIN_DEMOTED = "✅ បានបន្ថយ​អ្នកគ្រប់គ្រង {user_id} ទៅជាអ្នកប្រើប្រាស់"
ADMIN_NOT_FOUND = "⚠️ រកមិនឃើញអ្នកគ្រប់គ្រង {user_id}"
LAST_ADMIN_ERROR = "⛔ មិនអាចដកអ្នកគ្រប់គ្រងចុងក្រោយបានទេ។ សូមបន្ថែមអ្នកគ្រប់គ្រងម្នាក់ទៀតមុនសិន។"
TRUCK_ADDED = "✅ បានបន្ថែមឡាន {plate}"
TRUCK_REMOVED = "✅ បានដកឡាន {plate}"
TRUCK_NOT_FOUND = "⚠️ រកមិនឃើញឡាន {plate}"
VEHTYPE_ADDED = "✅ បានបន្ថែមប្រភេទយានយន្ត {name}"
VEHTYPE_REMOVED = "✅ បានដកប្រភេទយានយន្ត {name}"
VEHTYPE_NOT_FOUND = "⚠️ រកមិនឃើញប្រភេទយានយន្ត {name}"
BEGINNING_SET = "✅ បានកំណត់សមតុល្យដើមគ្រា {fuel} = {amount} លីត្រ សម្រាប់ខែ {month}"
INVALID_FUEL = "⚠️ ប្រភេទប្រេងមិនត្រឹមត្រូវ។ ត្រូវជា «ម៉ាស៊ូត» ឬ «ប្រេងសំាង»។"
INVALID_NUMBER = "⚠️ ចំនួនមិនត្រឹមត្រូវ។"

LIST_USERS_TITLE = "<b>បញ្ជីអ្នកប្រើប្រាស់៖</b>\n"
LIST_ADMINS_TITLE = "\n<b>បញ្ជីអ្នកគ្រប់គ្រង៖</b>\n"
LIST_TRUCKS_TITLE = "<b>បញ្ជីឡាន ({count})៖</b>\n"
LIST_VEHTYPES_TITLE = "<b>បញ្ជីប្រភេទយានយន្ត ({count})៖</b>\n"
LIST_EMPTY = "  (គ្មាន)"

SHEET_LINK = "🔗 តំណ Google Sheet៖\n{url}"

HELP_USER = (
    "<b>ពាក្យបញ្ជាសម្រាប់អ្នកប្រើប្រាស់៖</b>\n"
    "/start — ចាប់ផ្តើម\n"
    "/report — បំពេញរបាយការណ៍ថ្មី\n"
    "/datelog — កំណត់ថ្ងៃសម្រាប់​ការបញ្ចូលរបាយការណ៍\n"
    "/cancel — បោះបង់ការបំពេញ\n"
    "/help — ជំនួយ"
)

HELP_ADMIN = (
    "\n\n<b>ពាក្យបញ្ជាសម្រាប់អ្នកគ្រប់គ្រង៖</b>\n"
    "/adduser — បន្ថែមអ្នកប្រើប្រាស់\n"
    "/removeuser — ដកអ្នកប្រើប្រាស់\n"
    "/addadmin — បន្ថែមអ្នកគ្រប់គ្រង\n"
    "/removeadmin — បន្ថយអ្នកគ្រប់គ្រងទៅជាអ្នកប្រើ\n"
    "/listusers — បង្ហាញបញ្ជីអ្នកប្រើប្រាស់\n"
    "/addtruck — បន្ថែមឡាន\n"
    "/removetruck — ដកឡាន\n"
    "/listtrucks — បង្ហាញបញ្ជីឡាន\n"
    "/addvehicletype — បន្ថែមប្រភេទយានយន្ត\n"
    "/removevehicletype — ដកប្រភេទយានយន្ត\n"
    "/listvehicletypes — បង្ហាញបញ្ជីប្រភេទយានយន្ត\n"
    "/setbeginning — កំណត់សមតុល្យដើមគ្រា\n"
    "/setphone — កំណត់លេខទូរស័ព្ទអ្នកប្រើ\n"
    "/sheet — ទទួលតំណ Google Sheet"
)


def fmt_no_notes() -> str:
    return "—"
