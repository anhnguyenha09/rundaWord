import re
import unicodedata


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()
    nfd = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", stripped)

