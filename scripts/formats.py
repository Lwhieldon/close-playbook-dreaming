"""Writers for the file formats a close team actually shares. Used only to build the synthetic corpus.

- xlsx_report: a spreadsheet exported from the ERP's report grid: title rows, a selection line, the header,
  the data, and an optional totals row, the way users download reports to Excel.
- spool_txt: a fixed-width list printed to a spool file: page headers repeated every page, column rules.
- pdf_memo / docx_memo: signed policy memos as PDF, a draft as Word.
- bai2: a bank statement file in the BAI2 format banks send for cash reconciliation.

All content is fictional.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal as D
from pathlib import Path

PAGE_LINES = 58


def xlsx_report(
    path: Path,
    title: str,
    selection: list[str],
    columns: list[str],
    rows: list[dict],
    *,
    money: tuple[str, ...] = (),
    totals: tuple[str, ...] = (),
    sheets: list[tuple[str, list[str], list[dict]]] | None = None,
    sheet_name: str = "Report",
) -> None:
    """Write rows (dicts keyed by column) under SAP-style title and selection lines. `money` columns are
    written as numbers with two decimals; `totals` columns get a sum in a totals row. `sheets` adds more
    sheets as (name, selection lines, rows) with the same columns."""
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    for i, (name, sel, data) in enumerate([(sheet_name, selection, rows), *(sheets or [])]):
        if i:
            ws = wb.create_sheet()
        ws.title = name[:31]
        ws.append([title])
        ws["A1"].font = Font(bold=True)
        for line in sel:
            ws.append([line])
        ws.append([])
        ws.append(columns)
        for cell in ws[ws.max_row]:
            cell.font = Font(bold=True)
        for r in data:
            ws.append([_num(r.get(c, "")) if c in money else r.get(c, "") for c in columns])
            if money:
                for j, c in enumerate(columns, 1):
                    if c in money:
                        ws.cell(ws.max_row, j).number_format = "0.00"
        if totals and data:
            sums = {c: sum(_num(r.get(c, 0)) or 0 for r in data) for c in totals}
            ws.append(
                ["Total" if j == 0 else (round(sums[c], 2) if c in totals else "") for j, c in enumerate(columns)]
            )
            for j, c in enumerate(columns, 1):
                if c in totals:
                    ws.cell(ws.max_row, j).number_format = "0.00"
                    ws.cell(ws.max_row, j).font = Font(bold=True)
        for j, c in enumerate(columns, 1):
            ws.column_dimensions[ws.cell(len(sel) + 3, j).column_letter].width = max(10, min(48, len(c) + 4))
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.properties.creator = "SAP GUI export"
    wb.properties.created = datetime(2026, 1, 1)
    wb.properties.modified = datetime(2026, 1, 1)
    wb.save(path)
    _freeze(path)


def _num(v):
    if v in ("", None):
        return None
    return float(D(str(v).replace(",", "")))


def spool_txt(
    title: str, header_lines: list[str], columns: list[tuple[str, int]], rows: list[dict], footer: str
) -> str:
    """A fixed-width list as printed to a spool file, with the page header repeated on every page."""
    rule = "-" * (sum(w for _, w in columns) + len(columns) + 1)
    head = "|" + "|".join(f"{n[:w]:<{w}}" for n, w in columns) + "|"
    body = [
        "|"
        + "|".join(
            f"{str(r.get(n, ''))[:w]:>{w}}" if _numeric(r.get(n)) else f"{str(r.get(n, ''))[:w]:<{w}}"
            for n, w in columns
        )
        + "|"
        for r in rows
    ]
    per_page = PAGE_LINES - len(header_lines) - 5
    pages = [body[i : i + per_page] for i in range(0, len(body), per_page)] or [[]]
    out = []
    for n, chunk in enumerate(pages, 1):
        out.append(f"{title:<{len(rule) - 10}}Page {n:>4}")
        out += header_lines
        out += [rule, head, rule, *chunk, rule]
        if n < len(pages):
            out.append("\f")
    out.append(footer)
    return "\n".join(out) + "\n"


def _numeric(v) -> bool:
    try:
        float(str(v).replace(",", ""))
        return str(v).strip() != ""
    except ValueError:
        return False


def pdf_memo(path: Path, text: str, *, signed_by: str | None = None) -> None:
    from fpdf import FPDF

    pdf = FPDF(format="letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    lines = _latin1(text).splitlines()
    first = True
    for line in lines:
        if first:
            pdf.set_font("Helvetica", style="B", size=11)
            pdf.multi_cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", size=10)
            first = False
            continue
        if not line.strip():
            pdf.ln(3)
            continue
        indent = len(line) - len(line.lstrip(" "))
        pdf.set_x(pdf.l_margin + indent * 1.6)
        pdf.multi_cell(0, 5, line.strip(), new_x="LMARGIN", new_y="NEXT")
    if signed_by:
        pdf.ln(6)
        pdf.set_font("Helvetica", style="I", size=10)
        pdf.multi_cell(0, 5, f"Approved and signed electronically: {signed_by}", new_x="LMARGIN", new_y="NEXT")
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf.set_creation_date(datetime(2026, 1, 1))
    pdf.output(str(path))


def docx_memo(path: Path, text: str) -> None:
    import docx

    d = docx.Document()
    lines = text.splitlines()
    d.add_heading(lines[0], level=1)
    for line in lines[1:]:
        if line.strip():
            d.add_paragraph(line.strip(), style="List Bullet" if line.lstrip().startswith("- ") else None)
    for p in d.paragraphs:
        if p.text.startswith("- "):
            p.text = p.text[2:]
    d.core_properties.author = "Tarnwell Industries"
    d.core_properties.created = datetime(2026, 1, 1)
    d.core_properties.modified = datetime(2026, 1, 1)
    path.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(path))
    _freeze(path)


def _freeze(path: Path) -> None:
    """Pin the save timestamps inside an xlsx or docx so a rebuild writes byte-identical files."""
    import re
    import zipfile

    with zipfile.ZipFile(path) as z:
        parts = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    stamp = b"2026-11-01T00:00:00Z"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts:
            if name == "docProps/core.xml":
                data = re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*", rb"\g<1>" + stamp, data)
            z.writestr(zipfile.ZipInfo(name, date_time=(2026, 11, 1, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)


def _latin1(text: str) -> str:
    return text.replace("–", "-").replace("—", "-").replace("’", "'").encode("latin-1", "replace").decode("latin-1")


def bai2(
    *,
    sender: str,
    receiver: str,
    file_date: str,
    account: str,
    currency: str,
    opening: D,
    transactions: list[tuple[str, D, str, str]],
) -> str:
    """A BAI2 file with one account. transactions are (type code, amount, bank reference, text); amounts are
    positive, and the type code says credit (1xx-3xx) or debit (4xx-6xx)."""
    yymmdd = file_date[8:10] + file_date[0:2] + file_date[3:5]  # file_date is MM/DD/YYYY
    credits = sum(a for t, a, *_ in transactions if t < "400")
    debits = sum(a for t, a, *_ in transactions if t >= "400")
    closing = opening + credits - debits

    def cents(x: D) -> str:
        return str(int((x * 100).quantize(D("1"))))

    recs = [
        f"01,{sender},{receiver},{yymmdd},0600,1,,,2/",
        f"02,{receiver},{sender},1,{yymmdd},,{currency},2/",
        f"03,{account},{currency},010,{cents(opening)},,,015,{cents(closing)},,,"
        f"100,{cents(credits)},{sum(1 for t, *_ in transactions if t < '400')},,"
        f"400,{cents(debits)},{sum(1 for t, *_ in transactions if t >= '400')},/",
    ]
    for code, amt, ref, text in transactions:
        recs.append(f"16,{code},{cents(amt)},0,{ref},,/")
        recs.append(f"88,{text}")
    total = sum(int(cents(a)) for _, a, *_ in transactions) + int(cents(opening)) + int(cents(closing))
    n_acct = len(recs) - 2 + 1
    recs.append(f"49,{total},{n_acct}/")
    recs.append(f"98,{total},1,{n_acct + 2}/")
    recs.append(f"99,{total},1,{len(recs) + 1}/")
    return "\n".join(recs) + "\n"
