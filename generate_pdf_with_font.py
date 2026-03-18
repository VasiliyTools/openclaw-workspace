#!/usr/bin/env python3
"""
Генерация PDF с поддержкой кириллицы (шрифт DejaVu Sans).
"""

import sys
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib import colors

# Регистрируем шрифт DejaVu Sans
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
# Также зарегистрируем bold вариант
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(bold_path):
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_path))

def markdown_to_paragraphs(text, styles):
    elements = []
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('###'):
            elements.append(Paragraph(line[3:].strip(), styles['Heading3']))
        elif line.startswith('##'):
            elements.append(Paragraph(line[2:].strip(), styles['Heading2']))
        elif line.startswith('#'):
            elements.append(Paragraph(line[1:].strip(), styles['Heading1']))
        elif line.startswith('- '):
            elements.append(Paragraph('• ' + line[2:], styles['Normal']))
        else:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 6))
    return elements

def create_pdf(content, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Создаём стили с кириллическим шрифтом
    normal_style = ParagraphStyle(
        'NormalRu',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=10,
        leading=12
    )
    heading1_style = ParagraphStyle(
        'Heading1Ru',
        parent=styles['Heading1'],
        fontName='DejaVuSans-Bold' if 'DejaVuSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'DejaVuSans',
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    heading2_style = ParagraphStyle(
        'Heading2Ru',
        parent=styles['Heading2'],
        fontName='DejaVuSans-Bold' if 'DejaVuSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'DejaVuSans',
        fontSize=14,
        spaceAfter=8,
        textColor=colors.darkblue
    )
    heading3_style = ParagraphStyle(
        'Heading3Ru',
        parent=styles['Heading3'],
        fontName='DejaVuSans-Bold' if 'DejaVuSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'DejaVuSans',
        fontSize=12,
        spaceAfter=6,
        textColor=colors.darkblue
    )
    
    # Заменяем стандартные стили
    styles.add(normal_style)
    styles.add(heading1_style)
    styles.add(heading2_style)
    styles.add(heading3_style)
    
    elements = []
    elements.append(Paragraph("Отчёт Финансиста", heading1_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Используем наши стили
    custom_styles = {
        'Normal': normal_style,
        'Heading1': heading1_style,
        'Heading2': heading2_style,
        'Heading3': heading3_style
    }
    
    elements.extend(markdown_to_paragraphs(content, custom_styles))
    doc.build(elements)
    print(f"PDF создан: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: generate_pdf_with_font.py <входной_файл.md> <выходной_файл.pdf>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    create_pdf(content, output_file)