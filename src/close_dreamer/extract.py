"""Turn the file formats a close team actually shares into text an agent can read and search.

- .pdf   signed policy memos: the text layer, page by page (pypdf)
- .docx  memo drafts: paragraphs and tables (python-docx)
- .xlsx  spreadsheet exports from the ERP's report grid: every sheet, every non-empty row, cells joined
         with " | " so title rows, headers and totals stay visible (openpyxl)
- .txt, .dat, .vtt, .csv and other text: read as text. Older ERP spool files and bank files are often in
         the Windows code page, so UTF-8 is tried first, then cp1252.

The original files stay where they are; this is only how the dream and the evaluation read them. A real
deployment would add OCR for scanned PDFs, which have no text layer.
"""

from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache
from pathlib import Path

BINARY = {".pdf", ".docx", ".xlsx"}
TEXT = {".txt", ".md", ".json", ".jsonl", ".log", ".vtt", ".csv", ".dat"}
SUPPORTED = BINARY | TEXT


def text_of(path: Path) -> str:
    """The readable text of a corpus file. Cached by path, size and modification time."""
    path = Path(path)
    st = path.stat()
    return _cached(str(path.resolve()), st.st_size, st.st_mtime_ns)


@lru_cache(maxsize=512)
def _cached(path: str, _size: int, _mtime: int) -> str:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".pdf":
        return _pdf(p)
    if suffix == ".docx":
        return _docx(p)
    if suffix == ".xlsx":
        return _xlsx(p)
    return _plain(p)


def _plain(p: Path) -> str:
    data = p.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def _pdf(p: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(p))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n\n".join(f"[page {i}]\n{t}" for i, t in enumerate(pages, 1) if t)


def _docx(p: Path) -> str:
    import docx

    d = docx.Document(str(p))
    out = [para.text for para in d.paragraphs if para.text.strip()]
    for table in d.tables:
        for row in table.rows:
            out.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(out)


def _xlsx(p: Path) -> str:
    from openpyxl import load_workbook

    wb = load_workbook(str(p), read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        if len(wb.worksheets) > 1:
            out.append(f"[sheet {ws.title}]")
        for row in ws.iter_rows():
            cells = [_cell(c) for c in row]
            while cells and cells[-1] == "":
                cells.pop()
            if any(cells):
                out.append(" | ".join(cells))
    wb.close()
    return "\n".join(out)


def _cell(c) -> str:
    v = c.value
    if v is None:
        return ""
    if isinstance(v, datetime):
        return v.strftime("%m/%d/%Y") if v.time() == datetime.min.time() else v.strftime("%m/%d/%Y %H:%M:%S")
    if isinstance(v, date):
        return v.strftime("%m/%d/%Y")
    if isinstance(v, float | int) and not isinstance(v, bool):
        fmt = getattr(c, "number_format", "") or ""
        if "0.00" in fmt:
            return f"{v:,.2f}" if "," in fmt else f"{v:.2f}"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)
    return str(v).strip()
