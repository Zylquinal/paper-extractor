import os

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.hyperlink import Hyperlink

from src.exceptions import ExcelWriteError

MAIN_SHEET = "Paper Analysis"
Q_SHEET = "Questionnaires"
V_SHEET = "Variables"
R_SHEET = "Main References"

MAIN_HEADERS = ["Title", "Methodology & Research Object", "Main Result",
                "Limit / Research Gap", "Theory", "Q", "V", "R"]
Q_HEADERS = ["Paper Title", "Statement/Question", "Reference"]
V_HEADERS = ["Paper Title", "Variable Name", "Result", "References"]
R_HEADERS = ["Paper Title", "Reference Title", "Authors", "Explanation"]

ALL_SHEETS = [MAIN_SHEET, Q_SHEET, V_SHEET, R_SHEET]

HEADER_FILL = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
HEADER_FONT = Font(name="Arial", bold=True, size=11)
BODY_FONT = Font(name="Arial", size=11)
LINK_FONT = Font(name="Arial", size=11, color="0563C1", underline="single")
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
WRAP_ALIGNMENT = Alignment(wrap_text=True, vertical="top")

COLUMN_WIDTHS = {
    MAIN_SHEET: {"A": (20, 50), "B": (25, 65), "C": (25, 65), "D": (25, 65),
                 "E": (20, 40), "F": (3, 6), "G": (3, 6), "H": (3, 6)},
    Q_SHEET: {"A": (20, 50), "B": (30, 80), "C": (15, 40)},
    V_SHEET: {"A": (20, 50), "B": (20, 50), "C": (30, 80), "D": (15, 40)},
    R_SHEET: {"A": (20, 50), "B": (20, 50), "C": (20, 40), "D": (30, 80)},
}


def _style_header(ws, headers):
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center")


def _style_data_row(ws, row_num, num_cols):
    for col_idx in range(1, num_cols + 1):
        cell = ws.cell(row=row_num, column=col_idx)
        if not cell.hyperlink:
            cell.font = BODY_FONT
        cell.border = THIN_BORDER
        cell.alignment = WRAP_ALIGNMENT


def _auto_width(ws, headers, widths):
    for col_idx in range(1, len(headers) + 1):
        letter = get_column_letter(col_idx)
        min_w, max_w = widths.get(letter, (15, 60))
        max_len = 0
        for row in ws.iter_rows(min_col=col_idx, max_col=col_idx):
            for cell in row:
                if cell.value:
                    max_len = max(max_len, len(str(cell.value)))
        width = min(max(max_len + 2, min_w), max_w)
        ws.column_dimensions[letter].width = width


def _validate_headers(ws, headers):
    existing = []
    for col_idx in range(1, len(headers) + 1):
        existing.append(str(ws.cell(row=1, column=col_idx).value or ""))
    return existing == headers


def _validate_all_sheets(wb):
    sheets_headers = {
        MAIN_SHEET: MAIN_HEADERS,
        Q_SHEET: Q_HEADERS,
        V_SHEET: V_HEADERS,
        R_SHEET: R_HEADERS,
    }
    for name in sheets_headers:
        if name not in wb.sheetnames:
            raise ExcelWriteError(
                f"Sheet '{name}' not found in workbook. "
                f"Expected sheets: {list(sheets_headers.keys())}"
            )
    for name, headers in sheets_headers.items():
        ws = wb[name]
        if not _validate_headers(ws, headers):
            raise ExcelWriteError(
                f"Sheet '{name}' has different header format. "
                f"Expected: {headers}"
            )


def _apply_link(ws, row, col, location, display):
    cell = ws.cell(row=row, column=col)
    cell.value = display
    cell.hyperlink = Hyperlink(ref=cell.coordinate, location=location)
    cell.font = LINK_FONT
    cell.alignment = Alignment(horizontal="center", vertical="top")


def _init_sheet(ws, headers):
    for col_idx, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_idx, value=header)
    _style_header(ws, headers)


def _populate_main_sheet(ws, data, row, q_start, v_start, r_start):
    theory = ""
    if data.get("model") and data.get("model", {}).get("theory"):
        theory = "; ".join(data["model"]["theory"])

    values = [
        data.get("title", ""),
        data.get("methodology_object", ""),
        data.get("result", ""),
        data.get("limit_gap", ""),
        theory,
    ]
    for col, value in enumerate(values, 1):
        ws.cell(row=row, column=col, value=value)

    _style_data_row(ws, row, len(MAIN_HEADERS))

    if q_start:
        _apply_link(ws, row, 6, f"'{Q_SHEET}'!A{q_start}", "Q")
    if v_start:
        _apply_link(ws, row, 7, f"'{V_SHEET}'!A{v_start}", "V")
    if r_start:
        _apply_link(ws, row, 8, f"'{R_SHEET}'!A{r_start}", "R")


def _write_backlink(ws, row, title, main_row):
    cell = ws.cell(row=row, column=1)
    cell.value = title
    cell.hyperlink = Hyperlink(ref=cell.coordinate, location=f"'{MAIN_SHEET}'!A{main_row}")
    cell.font = LINK_FONT
    cell.alignment = WRAP_ALIGNMENT


def _populate_questionnaires(ws, data, start_row, main_row):
    items = data.get("questionnaires")
    if not items:
        return
    title = data.get("title", "")
    for i, item in enumerate(items):
        row = start_row + i
        ref = item.get("reference")
        if ref is None:
            ref_text = ""
        elif ref == "UNKNOWN":
            ref_text = "UNKNOWN"
        else:
            ref_text = str(ref)
        ws.cell(row=row, column=2, value=item.get("statement_question", ""))
        ws.cell(row=row, column=3, value=ref_text)
        _style_data_row(ws, row, len(Q_HEADERS))
        _write_backlink(ws, row, title, main_row)


def _populate_variables(ws, data, start_row, main_row):
    model = data.get("model")
    if not model or not model.get("variables"):
        return
    title = data.get("title", "")
    for i, var in enumerate(model["variables"]):
        row = start_row + i
        refs = var.get("references", [])
        ws.cell(row=row, column=2, value=var.get("name", ""))
        ws.cell(row=row, column=3, value=var.get("result", ""))
        ws.cell(row=row, column=4, value="; ".join(refs) if refs else "")
        _style_data_row(ws, row, len(V_HEADERS))
        _write_backlink(ws, row, title, main_row)


def _populate_references(ws, data, start_row, main_row):
    items = data.get("main_references")
    if not items:
        return
    title = data.get("title", "")
    for i, ref in enumerate(items):
        row = start_row + i
        ws.cell(row=row, column=2, value=ref.get("title", ""))
        ws.cell(row=row, column=3, value="; ".join(ref.get("authors", [])))
        ws.cell(row=row, column=4, value=ref.get("explanation", ""))
        _style_data_row(ws, row, len(R_HEADERS))
        _write_backlink(ws, row, title, main_row)


def _auto_width_all(wb):
    for name, headers in [(MAIN_SHEET, MAIN_HEADERS), (Q_SHEET, Q_HEADERS),
                          (V_SHEET, V_HEADERS), (R_SHEET, R_HEADERS)]:
        _auto_width(wb[name], headers, COLUMN_WIDTHS[name])


def _create_workbook(data: dict) -> Workbook:
    wb = Workbook()

    ws_main = wb.active
    ws_main.title = MAIN_SHEET
    _init_sheet(ws_main, MAIN_HEADERS)

    ws_q = wb.create_sheet(Q_SHEET)
    _init_sheet(ws_q, Q_HEADERS)

    ws_v = wb.create_sheet(V_SHEET)
    _init_sheet(ws_v, V_HEADERS)

    ws_r = wb.create_sheet(R_SHEET)
    _init_sheet(ws_r, R_HEADERS)

    main_row = 2

    has_q = bool(data.get("questionnaires"))
    has_v = bool(data.get("model") and data.get("model", {}).get("variables"))
    has_r = bool(data.get("main_references"))

    q_start = 2 if has_q else None
    v_start = 2 if has_v else None
    r_start = 2 if has_r else None

    _populate_main_sheet(ws_main, data, main_row, q_start, v_start, r_start)

    if has_q:
        _populate_questionnaires(ws_q, data, q_start, main_row)
    if has_v:
        _populate_variables(ws_v, data, v_start, main_row)
    if has_r:
        _populate_references(ws_r, data, r_start, main_row)

    _auto_width_all(wb)
    ws_main.freeze_panes = "A2"

    return wb


def write_result(data: dict, excel_path: str) -> None:
    if os.path.exists(excel_path):
        wb = load_workbook(excel_path)
        _validate_all_sheets(wb)

        ws_main = wb[MAIN_SHEET]
        main_row = ws_main.max_row + 1

        ws_q = wb[Q_SHEET]
        ws_v = wb[V_SHEET]
        ws_r = wb[R_SHEET]

        has_q = bool(data.get("questionnaires"))
        has_v = bool(data.get("model") and data.get("model", {}).get("variables"))
        has_r = bool(data.get("main_references"))

        q_start = ws_q.max_row + 1 if has_q else None
        v_start = ws_v.max_row + 1 if has_v else None
        r_start = ws_r.max_row + 1 if has_r else None

        _populate_main_sheet(ws_main, data, main_row, q_start, v_start, r_start)

        if has_q:
            _populate_questionnaires(ws_q, data, q_start, main_row)
        if has_v:
            _populate_variables(ws_v, data, v_start, main_row)
        if has_r:
            _populate_references(ws_r, data, r_start, main_row)

        _auto_width_all(wb)
    else:
        wb = _create_workbook(data)

    wb.save(excel_path)
