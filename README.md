# Daily Diesel/Gasoline Report Bot

Telegram bot (Khmer) for the company **accountant** to log fuel stock movements (received from suppliers, issued to trucks). Each entry is appended to a Google Sheet that mirrors the format of `1. Daily Report Diesel-1.xlsx` (per-month tabs, Khmer headers, running balance).

Designed for fast bulk entry: after each saved record the bot offers **Add similar / Add new / Done**, so logging 11 truck stock-out rows for one day takes ~3 taps each.

## Architecture

- **Language**: Khmer-only UI
- **Stack**: Python + `python-telegram-bot` (v21) + `gspread`
- **Storage**:
  - Google Sheet — one tab per month per fuel type (e.g. `ម៉ាស៊ូត Apr 2026`, `ប្រេងសំាង Apr 2026`)
  - Local JSON for whitelist, truck list, vehicle type list (in `data/`)
- **Access**: whitelist-based; only listed Telegram IDs can use the bot

## Quick start (already set up)

If `.env`, `service_account.json`, and `data/whitelist.json` are already in place:

```bash
cd /Users/het/Desktop/Projects/B-roth-project
python3 -m bot.main
```

You should see logs ending with `Application started`. Stop with **Ctrl+C**.

---

## First-time setup checklist

Do these in order. Steps 1–5 are one-time prep before the bot can start.

### 1. Create a Telegram bot

1. Open Telegram, message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`, follow the prompts
3. Copy the **bot token** it gives you
4. (Optional) Send `/setcommands` to BotFather to register the slash commands — paste:
   ```
   start - ចាប់ផ្តើម
   report - បំពេញរបាយការណ៍
   datelog - កំណត់ថ្ងៃរបាយការណ៍
   help - ជំនួយ
   cancel - បោះបង់
   ```

### 2. Create a Google service account

1. Go to <https://console.cloud.google.com/>
2. Create (or select) a project
3. Enable the **Google Sheets API** for that project
4. Go to *IAM & Admin → Service Accounts → Create Service Account*
5. After creating, click the account → *Keys → Add Key → Create new key → JSON*
6. Save the downloaded JSON file as `service_account.json` in the project root
7. **Important**: open the JSON, copy the `client_email` (looks like `xxx@xxx.iam.gserviceaccount.com`)

### 3. Create the target Google Sheet

1. Create a new Google Sheet (any name)
2. Click **Share** and share it with the service account email from step 2 — give **Editor** access
3. Copy **only the spreadsheet ID** from the URL — the long string between `/d/` and `/edit`:
   `https://docs.google.com/spreadsheets/d/`**`SPREADSHEET_ID`**`/edit`
   ⚠️ Don't paste the full URL into `GOOGLE_SHEET_ID` — only the ID portion.

### 4. Get your own Telegram user ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your numeric ID — save it

### 5. Configure `.env`

```bash
cp .env.example .env
# edit .env and fill in:
#   TELEGRAM_BOT_TOKEN=<token from step 1>
#   GOOGLE_SHEET_ID=<id from step 3, NOT the full URL>
```

### 6. Install dependencies

The simplest path on macOS that's known to work:

```bash
pip3 install -r requirements.txt --break-system-packages
```

<details>
<summary>Optional: use a virtual environment instead</summary>

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
On some macOS Python builds `python3 -m venv` fails with an `ensurepip` error — in that case, fall back to `--break-system-packages` above, or install [`uv`](https://github.com/astral-sh/uv) and run `uv venv && source .venv/bin/activate && uv pip install -r requirements.txt`.
</details>

### 7. Bootstrap your admin account

The whitelist starts empty. To make yourself the first admin, edit `data/whitelist.json` directly **once**:

```json
{
  "admins": [
    {"id": 123456789, "name": "Your Name"}
  ],
  "users": []
}
```

Use the numeric Telegram ID from step 4. Then start the bot.

### 8. Run the bot

```bash
python3 -m bot.main
```

Expected output:
```
[INFO] telegram.ext.Application: Application started
[INFO] httpx: ... getUpdates "HTTP/1.1 200 OK"
```

Open Telegram → find your bot → send `/start`. You'll be asked to tap **📞 ចែករំលែកលេខទូរស័ព្ទ** once to register your phone, then the **📝 បំពេញរបាយការណ៍** menu appears.

From there, manage everyone else via bot commands:
- `/adduser <id> <name>` — add a regular employee
- `/addadmin <id> <name>` — add another admin
- `/listusers` — show the whitelist

## User flow (Khmer)

1. Accountant sends `/start` → bot greets in Khmer
2. **First time only**: bot asks the user to tap **📞 ចែករំលែកលេខទូរស័ព្ទ** to share their phone number. The phone is saved to `whitelist.json` and reused forever after — never asked again.
3. Bot shows the **បំពេញរបាយការណ៍** button. The flow then **branches by operation type**:

### Stock In (ចូល) — fuel received from supplier
ប្រភេទប្រេង → **ចូល** → បរិមាណ → **ប្រភព** (paying company) → ផ្សេងៗ → confirm

### Stock Out (ចេញ) — fuel issued to a truck
ប្រភេទប្រេង → **ចេញ** → ប្រភេទយានយន្ត → ឡាន → បរិមាណ → ផ្សេងៗ → confirm

After confirm, the bot offers three buttons:

| Button | Behaviour |
|---|---|
| ➕ **ដូចគ្នា** (Add similar) | Same fuel + same operation + same vehicle type — jumps directly to truck/amount step |
| 🔄 **ថ្មី** (Add new) | Full restart with fresh fuel/operation selection |
| 🏁 **បញ្ចប់** (Done) | End the session |

### Backdating with `/datelog`
By default, every entry uses today's date. To backdate a session (e.g., catching up on yesterday's logs):

```
/datelog 2026-04-25       set date for the current chat
/datelog show             check what date is currently active
/datelog reset            revert to today
```

## Admin commands

| Command | Purpose |
|---|---|
| `/adduser <id> <name>` | Add employee to whitelist |
| `/addadmin <id> <name>` | Promote to admin |
| `/removeuser <id>` | Remove from whitelist |
| `/listusers` | Show all users + admins |
| `/addtruck <plate>` | Add truck to picklist |
| `/removetruck <plate>` | Remove truck |
| `/addvehicletype <name>` | Add vehicle type (e.g. `ឡានដឹក`) |
| `/removevehicletype <name>` | Remove vehicle type |
| `/setbeginning <ម៉ាស៊ូត\|ប្រេងសំាង> <amount>` | Set opening balance for current month |
| `/setphone <id> <phone>` | Manually set/override a user's phone number |
| `/sheet` | Get the Google Sheet URL |

## Sheet behavior

- New month tabs are auto-created on first entry, with the same template as the original file (title, super-headers, sub-headers, opening row, totals at row 36, beginning/ending balance at rows 37–38).
- Running total formula in column I = `previous_total + IN - OUT` (fixes the bug in the original sheet, where Stock In didn't update the running balance).
- Opening balance (F4) defaults to 0 — set it via `/setbeginning` at the start of each month.

### Column layout

| Col | Khmer header | Content |
|---|---|---|
| A | ល.រ | Sequence # within the month |
| B | ថ្ងៃ ខែ ឆ្នាំ | Date (auto = today; override with `/datelog`) |
| C | ឈ្មោះសម្ភារៈ | Vehicle type (e.g. ឡានទឹក, ឡានដឹក) |
| D | លេខឡាន | Truck number |
| E | ផ្លាកលេខឡាន | License plate |
| F | ដើមគ្រា | Beginning balance (opening row only) |
| G | ចូល | Stock In (received) |
| H | ចេញ | Stock Out (issued) |
| I | ស្តុកសរុប | Running total (formula) |
| J | ផ្សេងៗ | User-entered notes |
| K | អ្នកបំពេញ | Submitter's full name (Telegram first + last) |
| L | គណនី Telegram | Submitter's @username |
| M | លេខទូរស័ព្ទ | Submitter's phone number |
| N | ប្រភព | Source / supplier — paying company (Stock In only; empty for Stock Out) |

## Hosting

Local for testing. For 24/7:
- **Railway** or **Render** free tier — push the repo, set env vars, point at `python -m bot.main`
- **Your own VPS** — run with `systemd` or a tmux session
- Use long-polling (default); no public URL required

## Project layout

```
.
├── bot/
│   ├── main.py            # entry point
│   ├── config.py          # env vars
│   ├── i18n.py            # all Khmer strings
│   ├── sheets.py          # Google Sheets logic
│   ├── storage.py         # JSON persistence
│   └── handlers/
│       ├── start.py       # /start, /help, whitelist guard, contact share
│       ├── report.py      # branched conversation flow + Add another loop
│       ├── datelog.py     # /datelog backdate command
│       └── admin.py       # admin commands
├── data/
│   ├── trucks.json
│   ├── vehicle_types.json
│   └── whitelist.json
├── 1. Daily Report Diesel-1.xlsx   # original template (reference)
├── requirements.txt
├── .env.example
└── README.md
```
