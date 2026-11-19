"""
Fayllarni (Word .docx, PDF .pdf, Excel .xlsx, PowerPoint .pptx, Text .txt va boshqalar)
qayta ishlab, ulardagi matnlarni Kirill <-> Yangi Lotin / Klassik Lotin o'giruvchi modul.
"""

import os
import io
import shutil
import charset_normalizer
from docx import Document
from pypdf import PdfReader
import openpyxl
from pptx import Presentation

# ReportLab kutubxonasi - PDF generatsiya qilish uchun
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from translit import (
    auto_transliterate,
    cyrillic_to_latin,
    latin_to_cyrillic,
    classic_to_new_latin,
    new_to_classic_latin,
    detect_script
)

# Windows Arial shriftini ulash (Kirill, Yangi Lotin: Ö, Ğ, Ş, Ç va barchasini to'liq ko'rsatish uchun)
FONT_NAME = 'Helvetica'
try:
    windows_arial = 'C:/Windows/Fonts/arial.ttf'
    if os.path.exists(windows_arial):
        pdfmetrics.registerFont(TTFont('UzbekArial', windows_arial))
        FONT_NAME = 'UzbekArial'
except Exception:
    pass


def get_translit_func(mode: str, sample_text: str = ""):
    """
    Belgilangan rejimga mos o'girish funksiyasini va yo'nalish nomini qaytaradi.
    mode:
      - 'auto': avtomatik aniqlash (Kirill -> Yangi Lotin, Lotin -> Kirill)
      - 'new_latin': Kirill -> Yangi Lotin (Ö, Ğ, Ş, Ç)
      - 'classic_latin': Kirill -> Klassik Lotin (Oʻ, Gʻ, Sh, Ch)
      - 'cyrillic': Lotin -> Kirill
      - 'classic_to_new': Klassik Lotin -> Yangi Lotin
      - 'new_to_classic': Yangi Lotin -> Klassik Lotin
    """
    if mode == 'new_latin':
        current = detect_script(sample_text)
        if current == 'cyrillic':
            return (lambda t: cyrillic_to_latin(t, alphabet_version='new')), 'Kirill ➡️ Yangi Lotin'
        else:
            return classic_to_new_latin, 'Klassik Lotin ➡️ Yangi Lotin'

    elif mode == 'classic_latin':
        current = detect_script(sample_text)
        if current == 'cyrillic':
            return (lambda t: cyrillic_to_latin(t, alphabet_version='classic')), 'Kirill ➡️ Klassik Lotin'
        else:
            return new_to_classic_latin, 'Yangi Lotin ➡️ Klassik Lotin'

    elif mode == 'cyrillic':
        return latin_to_cyrillic, 'Lotin ➡️ Kirill'

    elif mode == 'classic_to_new':
        return classic_to_new_latin, 'Klassik Lotin ➡️ Yangi Lotin'

    elif mode == 'new_to_classic':
        return new_to_classic_latin, 'Yangi Lotin ➡️ Klassik Lotin'

    else:
        # Avto rejim
        current = detect_script(sample_text)
        if current == 'cyrillic':
            return (lambda t: cyrillic_to_latin(t, alphabet_version='new')), 'Kirill ➡️ Yangi Lotin'
        elif current == 'new_latin':
            return latin_to_cyrillic, 'Yangi Lotin ➡️ Kirill'
        else:
            return latin_to_cyrillic, 'Lotin ➡️ Kirill'


def process_docx(input_path: str, output_path: str, mode: str = 'auto') -> tuple[str, str]:
    """
    Word (.docx) faylini formatlarini saqlagan holda o'giradi.
    """
    doc = Document(input_path)

    # Rejimni aniqlash uchun namuna matn olish
    sample_text = ""
    for p in doc.paragraphs:
        if p.text.strip():
            sample_text += " " + p.text.strip()
            if len(sample_text) > 200:
                break

    translit_func, direction = get_translit_func(mode, sample_text)

    def convert_runs(paragraph):
        for run in paragraph.runs:
            if run.text:
                run.text = translit_func(run.text)
        if not paragraph.runs and paragraph.text:
            paragraph.text = translit_func(paragraph.text)

    # 1. Paragraflarni o'girish
    for p in doc.paragraphs:
        convert_runs(p)

    # 2. Jadvallardagi matnlarni o'girish
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    convert_runs(p)

    # 3. Sarlavha (Header) va quyi qismlar (Footer)
    for section in doc.sections:
        for p in section.header.paragraphs:
            convert_runs(p)
        for p in section.footer.paragraphs:
            convert_runs(p)

    doc.save(output_path)
    return output_path, direction


def process_pdf(input_path: str, output_pdf_path: str, output_docx_path: str = None, mode: str = 'auto') -> tuple[list[str], str]:
    """
    PDF faylidagi matnlarni o'qib, o'girilgan yangi PDF va Word (.docx) yaratadi.
    """
    reader = PdfReader(input_path)
    full_text_pages = []

    for page in reader.pages:
        txt = page.extract_text() or ""
        full_text_pages.append(txt)

    all_text = "\n".join(full_text_pages).strip()
    if not all_text:
        raise ValueError("PDF fayldan matn ajratib olinmadi. Bu fayl skaner qilingan rasm bo'lishi mumkin.")

    translit_func, direction = get_translit_func(mode, all_text[:300])

    # 1. Yangi PDF yaratish (ReportLab)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'UzbekStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=11,
        leading=15,
        spaceAfter=6
    )

    story = []
    for page_idx, page_text in enumerate(full_text_pages):
        converted_page = translit_func(page_text)
        paragraphs = converted_page.split('\n')
        for line in paragraphs:
            clean_line = line.strip()
            if clean_line:
                safe_line = clean_line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(safe_line, normal_style))
            else:
                story.append(Spacer(1, 4))
        if page_idx < len(full_text_pages) - 1:
            story.append(Spacer(1, 14))

    doc.build(story)
    generated_files = [output_pdf_path]

    # 2. Tahrirlash uchun Word (.docx) faylini ham tayyorlash
    if output_docx_path:
        word_doc = Document()
        for page_text in full_text_pages:
            converted_page = translit_func(page_text)
            for line in converted_page.split('\n'):
                word_doc.add_paragraph(line)
        word_doc.save(output_docx_path)
        generated_files.append(output_docx_path)

    return generated_files, direction


def process_txt(input_path: str, output_path: str, mode: str = 'auto') -> tuple[str, str]:
    """
    Oddiy matnli fayllarni (.txt, .srt, .csv, .md, .json va h.k.) o'giradi.
    """
    matches = charset_normalizer.from_path(input_path)
    best_match = matches.best()
    encoding = best_match.encoding if best_match else 'utf-8'

    with open(input_path, 'r', encoding=encoding, errors='replace') as f:
        content = f.read()

    translit_func, direction = get_translit_func(mode, content[:300])
    converted_content = translit_func(content)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(converted_content)

    return output_path, direction


def process_xlsx(input_path: str, output_path: str, mode: str = 'auto') -> tuple[str, str]:
    """
    Excel (.xlsx) faylini o'giradi.
    """
    wb = openpyxl.load_workbook(input_path)

    sample_text = ""
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            for val in row:
                if isinstance(val, str) and val.strip():
                    sample_text += " " + val.strip()
                    if len(sample_text) > 200:
                        break
            if len(sample_text) > 200:
                break
        if len(sample_text) > 200:
            break

    translit_func, direction = get_translit_func(mode, sample_text)

    for sheet in wb.worksheets:
        try:
            sheet.title = translit_func(sheet.title)[:31]
        except Exception:
            pass

        for row in sheet.iter_rows():
            for cell in row:
                if isinstance(cell.value, str) and cell.value:
                    cell.value = translit_func(cell.value)

    wb.save(output_path)
    return output_path, direction


def process_pptx(input_path: str, output_path: str, mode: str = 'auto') -> tuple[str, str]:
    """
    PowerPoint (.pptx) taqdimot faylini o'giradi.
    """
    prs = Presentation(input_path)

    sample_text = ""
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                txt = shape.text_frame.text.strip()
                if txt:
                    sample_text += " " + txt
                    if len(sample_text) > 200:
                        break
        if len(sample_text) > 200:
            break

    translit_func, direction = get_translit_func(mode, sample_text)

    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    for r in p.runs:
                        if r.text:
                            r.text = translit_func(r.text)
            if shape.has_table:
                for row in shape.table.rows:
                    for cell in row.cells:
                        for p in cell.text_frame.paragraphs:
                            for r in p.runs:
                                if r.text:
                                    r.text = translit_func(r.text)

    prs.save(output_path)
    return output_path, direction


def convert_any_file(input_path: str, output_dir: str, original_filename: str, mode: str = 'auto') -> tuple[list[str], str]:
    """
    Har qanday faylni tegishli konvertorga yo'naltiradi.
    """
    os.makedirs(output_dir, exist_ok=True)
    base_name, ext = os.path.splitext(original_filename)
    ext_lower = ext.lower()

    suffix_map = {
        'new_latin': '_yangi_lotin',
        'classic_latin': '_eski_lotin',
        'cyrillic': '_kirill',
        'classic_to_new': '_yangi_lotin',
        'new_to_classic': '_eski_lotin',
        'auto': '_ugirilgan'
    }
    suffix = suffix_map.get(mode, '_ugirilgan')

    if ext_lower in ('.docx', '.doc'):
        if ext_lower == '.doc':
            raise ValueError("Eski .doc formati qo'llab-quvvatlanmaydi. Iltimos, uni Word dasturida ochib, zamonaviy .docx formatida saqlang va qayta yuboring.")
        out_name = f"{base_name}{suffix}.docx"
        out_path = os.path.join(output_dir, out_name)
        res_file, direction = process_docx(input_path, out_path, mode)
        return [res_file], direction

    elif ext_lower == '.pdf':
        out_pdf_name = f"{base_name}{suffix}.pdf"
        out_docx_name = f"{base_name}{suffix}.docx"
        out_pdf_path = os.path.join(output_dir, out_pdf_name)
        out_docx_path = os.path.join(output_dir, out_docx_name)
        files, direction = process_pdf(input_path, out_pdf_path, out_docx_path, mode)
        return files, direction

    elif ext_lower == '.xlsx':
        out_name = f"{base_name}{suffix}.xlsx"
        out_path = os.path.join(output_dir, out_name)
        res_file, direction = process_xlsx(input_path, out_path, mode)
        return [res_file], direction

    elif ext_lower == '.pptx':
        out_name = f"{base_name}{suffix}.pptx"
        out_path = os.path.join(output_dir, out_name)
        res_file, direction = process_pptx(input_path, out_path, mode)
        return [res_file], direction

    elif ext_lower in ('.txt', '.csv', '.srt', '.md', '.json', '.xml', '.html', '.py', '.js', '.css', '.log'):
        out_name = f"{base_name}{suffix}{ext}"
        out_path = os.path.join(output_dir, out_name)
        res_file, direction = process_txt(input_path, out_path, mode)
        return [res_file], direction

    else:
        out_name = f"{base_name}{suffix}{ext}"
        out_path = os.path.join(output_dir, out_name)
        try:
            res_file, direction = process_txt(input_path, out_path, mode)
            return [res_file], direction
        except Exception:
            raise ValueError(f"'{ext}' formatidagi fayllar matn sifatida qayta ishlanmadi.")
