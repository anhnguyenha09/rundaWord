import csv
import io


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def parse_vocab_file(file_content: bytes, filename: str):
    words: list[tuple[str, str]] = []
    ext = filename.rsplit(".", 1)[1].lower()
    if ext == "csv":
        try:
            text = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = file_content.decode("latin-1")
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        start = 0
        if rows and rows[0] and rows[0][0].strip().lower() in ["english", "tiếng anh", "word_en", "từ tiếng anh", "en"]:
            start = 1
        for row in rows[start:]:
            if len(row) >= 2:
                en, vi = row[0].strip(), row[1].strip()
                if en and vi:
                    words.append((en, vi))
    elif ext in ("xlsx", "xls"):
        try:
            import openpyxl

            wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True)
            ws = wb.active
            first = True
            for row in ws.iter_rows(values_only=True):
                if first:
                    first = False
                    if row and row[0] and str(row[0]).strip().lower() in [
                        "english",
                        "tiếng anh",
                        "word_en",
                        "từ tiếng anh",
                        "en",
                    ]:
                        continue
                if row and len(row) >= 2 and row[0] and row[1]:
                    en, vi = str(row[0]).strip(), str(row[1]).strip()
                    if en and vi:
                        words.append((en, vi))
        except Exception as e:
            return f"Lỗi đọc file Excel: {str(e)}"

    if not words:
        return "File không có dữ liệu hợp lệ"
    return words

