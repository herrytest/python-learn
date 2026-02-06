from pathlib import Path

import pytesseract
from PIL import Image

from app.core.config import get_settings

settings = get_settings()

if settings.tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def extract_text_from_image(image_path: str) -> str:
    path = Path(image_path)
    if not path.exists():
        return ""

    with Image.open(path) as img:
        text = pytesseract.image_to_string(img)
    return text.strip()
