import os
import pypdfium2 as pdfium
from markitdown import MarkItDown
from rapidocr_onnxruntime import RapidOCR

_ocr_engine = None

def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine

def extract_text_from_scanned_pdf(pdf_path: str) -> str:
    """Merender tiap halaman PDF menjadi gambar lalu mengekstrak teks dengan OCR."""
    ocr = get_ocr_engine()
    pdf = pdfium.PdfDocument(pdf_path)
    pages_markdown = []

    try:
        for idx in range(len(pdf)):
            page = pdf[idx]
            # Render skala 2.0 (~144 DPI) agar huruf kecil terbaca jelas namun tetap cepat
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()

            result, _ = ocr(pil_image)
            if result:
                lines = [item[1] for item in result if item[1].strip()]
                page_text = "\n".join(lines)
                pages_markdown.append(f"## Halaman {idx + 1}\n\n{page_text}")
    finally:
        pdf.close()

    return "\n\n".join(pages_markdown)

def convert_document(file_path: str, converter: MarkItDown, force_ocr: bool = False) -> tuple[str, bool]:
    """
    Mengonversi dokumen ke Markdown.
    Mengembalikan tuple: (teks_markdown, apakah_menggunakan_ocr)
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf" and force_ocr:
        return extract_text_from_scanned_pdf(file_path), True

    result = converter.convert(file_path)
    md_text = (result.text_content or "").strip()

    # Jika file adalah PDF dan teks yang terbaca sangat minim (< 50 karakter), jalankan OCR otomatis
    if ext == ".pdf" and len(md_text) < 50:
        ocr_text = extract_text_from_scanned_pdf(file_path)
        if ocr_text.strip():
            return ocr_text, True

    return md_text, False