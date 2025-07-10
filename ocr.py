import pytesseract
from pdf2image import convert_from_path
from PIL import Image

def ocr_from_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)

def extract_text_with_ocr(file_path: str) -> str:
    try:
        pages = convert_from_path(file_path)
        return "\n".join(ocr_from_image(p) for p in pages)
    except Exception:
        return ""