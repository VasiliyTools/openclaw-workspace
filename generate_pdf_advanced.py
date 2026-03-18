#!/usr/bin/env python3
"""
Генерация PDF с поддержкой кириллицы и Markdown-таблиц.
"""

import sys
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

# Регистрируем шрифты
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(bold_path):
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold_path))

def parse_markdown_table(table_text):
    """Парсит Markdown-таблицу и возвращает данные для reportlab Table."""
    lines = [line.strip() for line in table_text.split('\n') if line.strip()]
    if len(lines) < 2:
        return None
    # Первая строка - заголовки
    headers = [cell.strip() for cell in lines[0].split('|') if cell.strip()]
    # Вторая строка - разделитель (игнорируем)
    data = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        if len(cells) == len(headers):
            data.append(cells)
    return headers, data

def markdown_to_elements(text, styles):
    """Преобразует Markdown-текст в список элементов reportlab."""
    elements = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        # Пропускаем пустые строки
        if not line:
            i += 1
            continue
        
        # Таблица: ищем последовательность строк, начинающихся с '|'
        if line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            table_text = '\n'.join(table_lines)
            parsed = parse_markdown_table(table_text)
            if parsed:
                headers, data = parsed
                # Создаём таблицу
                table_data = [headers] + data
                # Стиль таблицы
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 12))
            continue
        
        # Заголовки
        if line.startswith('###'):
            elements.append(Paragraph(line[3:].strip(), styles['Heading3']))
        elif line.startswith('##'):
            elements.append(Paragraph(line[2:].strip(), styles['Heading2']))
        elif line.startswith('#'):
            elements.append(Paragraph(line[1:].strip(), styles['Heading1']))
        # Маркированные списки
        elif line.startswith('- '):
            elements.append(Paragraph('• ' + line[2:], styles['Normal']))
        else:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 6))
        i += 1
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
    
    styles.add(normal_style)
    styles.add(heading1_style)
    styles.add(heading2_style)
    styles.add(heading3_style)
    
    custom_styles = {
        'Normal': normal_style,
        'Heading1': heading1_style,
        'Heading2': heading2_style,
        'Heading3': heading3_style
    }
    
    elements = []
    elements.append(Paragraph("Отчёт Финансиста", heading1_style))
    elements.append(Spacer(1, 0.25*inch))
    
    elements.extend(markdown_to_elements(content, custom_styles))
    doc.build(elements)
    print(f"PDF создан: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: generate_pdf_advanced.py <входной_файл.md> <выходной_файл.pdf>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    create_pdf(content, output_file)