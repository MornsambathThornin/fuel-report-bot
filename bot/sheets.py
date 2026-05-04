"""Google Sheets integration: per-month tabs matching the original report format."""
from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass
from typing import Optional
from zoneinfo import ZoneInfo

import gspread
from google.oauth2.service_account import Credentials

from . import config, i18n

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Column layout (1-indexed):
# A=No, B=Date, C=VehicleType, D=TruckNo, E=Plate,
# F=Beginning, G=StockIn, H=StockOut, I=Total, J=Notes,
# K=SubmitterName, L=Username, M=Phone, N=Source
COL_NO, COL_DATE, COL_VTYPE, COL_TNO, COL_PLATE = 1, 2, 3, 4, 5
COL_BEGIN, COL_IN, COL_OUT, COL_TOTAL, COL_NOTES = 6, 7, 8, 9, 10
COL_SUBMITTER, COL_USERNAME, COL_PHONE, COL_SOURCE = 11, 12, 13, 14
DATA_START_ROW = 5  # row 4 is the opening-balance row


@dataclass
class Entry:
    fuel_type: str           # "ម៉ាស៊ូត" or "ប្រេងសំាង"
    operation: str           # "ចូល" or "ចេញ"
    amount: float
    notes: str
    date: dt.date
    submitter_name: str      # Telegram first + last name (e.g. "Thornin Mornsambath")
    submitter_username: str  # Telegram @username (or "")
    submitter_phone: str     # phone number (or "")
    # Stock Out fields (empty for Stock In)
    vehicle_type: str = ""
    truck_no: int = 0
    plate: str = ""
    # Stock In field (empty for Stock Out)
    source: str = ""


_client: Optional[gspread.Client] = None


def _get_client() -> gspread.Client:
    global _client
    if _client is None:
        if config.GOOGLE_SERVICE_ACCOUNT_JSON:
            info = json.loads(config.GOOGLE_SERVICE_ACCOUNT_JSON)
            creds = Credentials.from_service_account_info(info, scopes=_SCOPES)
        else:
            creds = Credentials.from_service_account_file(
                config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=_SCOPES
            )
        _client = gspread.authorize(creds)
    return _client


def _spreadsheet():
    return _get_client().open_by_key(config.GOOGLE_SHEET_ID)


def now_local() -> dt.datetime:
    return dt.datetime.now(ZoneInfo(config.TIMEZONE))


def _tab_name(fuel_type: str, when: dt.date) -> str:
    return f"{fuel_type} {when.strftime('%b %Y')}"


def sheet_url() -> str:
    return f"https://docs.google.com/spreadsheets/d/{config.GOOGLE_SHEET_ID}"


def _ensure_tab(fuel_type: str, when: dt.date) -> gspread.Worksheet:
    """Return the worksheet for (fuel_type, month-of-when), creating it if needed."""
    ss = _spreadsheet()
    name = _tab_name(fuel_type, when)
    try:
        return ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=name, rows=200, cols=16)
        _initialize_template(ws, fuel_type, when)
        return ws


def _initialize_template(ws: gspread.Worksheet, fuel_type: str, when: dt.date) -> None:
    """Write title, headers, opening row, and totals/balance section."""
    month_kh = _khmer_month(when.month)
    year_kh = _khmer_digits(str(when.year))

    title = (
        f"{config.COMPANY_NAME_KH}\n"
        f"បញ្ជីប្រើប្រាស់ប្រេង{fuel_type}ប្រចាំខែ{month_kh} ឆ្នាំ {year_kh}"
    )

    ws.update_cell(1, 1, title)
    ws.merge_cells("A1:N1")

    # Header row 2 (super-headers)
    ws.update_cell(2, COL_NO, "ល.រ")
    ws.update_cell(2, COL_DATE, "ថ្ងៃ ខែ ឆ្នាំ")
    ws.update_cell(2, COL_VTYPE, "ឈ្មោះសម្ភារៈ")
    ws.update_cell(2, COL_TNO, "លេខឡាន")
    ws.update_cell(2, COL_PLATE, "ផ្លាកលេខឡាន")
    ws.update_cell(2, COL_BEGIN, "សម្ភារៈ")
    ws.update_cell(2, COL_SUBMITTER, "អ្នកបំពេញ")
    ws.update_cell(2, COL_USERNAME, "គណនី Telegram")
    ws.update_cell(2, COL_PHONE, "លេខទូរស័ព្ទ")
    ws.update_cell(2, COL_SOURCE, "ប្រភព")
    ws.merge_cells("A2:A3")
    ws.merge_cells("B2:B3")
    ws.merge_cells("C2:C3")
    ws.merge_cells("D2:D3")
    ws.merge_cells("E2:E3")
    ws.merge_cells("F2:J2")
    ws.merge_cells("K2:K3")
    ws.merge_cells("L2:L3")
    ws.merge_cells("M2:M3")
    ws.merge_cells("N2:N3")

    # Header row 3 (sub-headers under "សម្ភារៈ")
    ws.update_cell(3, COL_BEGIN, "ដើមគ្រា")
    ws.update_cell(3, COL_IN, "ចូល")
    ws.update_cell(3, COL_OUT, "ចេញ")
    ws.update_cell(3, COL_TOTAL, "ស្តុកសរុប")
    ws.update_cell(3, COL_NOTES, "ផ្សេងៗ")

    # Opening-balance row (row 4)
    ws.update_cell(4, COL_DATE, when.replace(day=1).isoformat())
    ws.update_cell(4, COL_VTYPE, "បរិមាណប្រេងដើមគ្រា")
    ws.update_cell(4, COL_BEGIN, 0)
    ws.update_cell(4, COL_TOTAL, "=F4")

    # Totals/balance section (start at row 36 like the original; will be moved if data grows past it)
    ws.update_cell(36, COL_NO, "Total")
    ws.merge_cells("A36:E36")
    ws.update_cell(36, COL_BEGIN, "=SUM(F4:F35)")
    ws.update_cell(36, COL_IN, "=SUM(G4:G35)")
    ws.update_cell(36, COL_OUT, "=SUM(H4:H35)")

    ws.update_cell(37, COL_NO, "Beginning Balance")
    ws.merge_cells("A37:E37")
    ws.update_cell(37, COL_BEGIN, "=F36")
    ws.merge_cells("F37:H37")

    ws.update_cell(38, COL_NO, "Ending Balance")
    ws.merge_cells("A38:E38")
    ws.update_cell(38, COL_BEGIN, "=F37+G36-H36")
    ws.merge_cells("F38:H38")


def _khmer_digits(s: str) -> str:
    table = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")
    return s.translate(table)


def _khmer_month(m: int) -> str:
    months = [
        "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
        "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ",
    ]
    return months[m - 1]


def _next_data_row(ws: gspread.Worksheet) -> int:
    """First empty row in the data area (row 5 onward, before the totals at row 36)."""
    col_a = ws.col_values(COL_NO)
    # Find max row with data in column A or B in the data area
    last = DATA_START_ROW - 1
    for i, val in enumerate(col_a, start=1):
        if DATA_START_ROW <= i < 36 and val not in (None, ""):
            last = i
    return last + 1


def append_entry(entry: Entry) -> int:
    """Append a row for this entry. Returns the row number written."""
    ws = _ensure_tab(entry.fuel_type, entry.date)
    row = _next_data_row(ws)
    seq = row - DATA_START_ROW + 1  # 1-based sequence # within the month

    notes_cell = (entry.notes or "").strip() or i18n.fmt_no_notes()

    in_amt = entry.amount if entry.operation == i18n.OP_IN else ""
    out_amt = entry.amount if entry.operation == i18n.OP_OUT else ""

    prev = row - 1
    total_formula = f"=N(I{prev})+N(G{row})-N(H{row})"

    username_cell = f"@{entry.submitter_username}" if entry.submitter_username else ""
    truck_no_cell = entry.truck_no if entry.truck_no else ""

    values = [
        seq,
        entry.date.isoformat(),
        entry.vehicle_type,
        truck_no_cell,
        entry.plate,
        "",                          # F: beginning (only set on opening row)
        in_amt,                      # G
        out_amt,                     # H
        total_formula,               # I
        notes_cell,                  # J
        entry.submitter_name,        # K
        username_cell,               # L
        entry.submitter_phone,       # M
        entry.source,                # N
    ]
    ws.update(
        f"A{row}:N{row}",
        [values],
        value_input_option="USER_ENTERED",
    )
    return row


def set_beginning_balance(fuel_type: str, amount: float, when: Optional[dt.date] = None) -> str:
    """Set the opening balance (F4) for the given fuel type and month."""
    when = when or now_local().date()
    ws = _ensure_tab(fuel_type, when)
    ws.update_cell(4, COL_BEGIN, amount)
    return _tab_name(fuel_type, when)
