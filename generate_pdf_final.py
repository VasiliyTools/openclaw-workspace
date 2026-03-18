#!/usr/bin/env python3
"""
Генерация PDF с корректными таблицами (перенос слов, ограничение ширины).
"""

import sys
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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

def create_table(headers, data, available_width):
    """Создаёт таблицу с переносом слов и ограничением ширины."""
    # Преобразуем все ячейки в Paragraph для переноса
    from reportlab.lib.styles import ParagraphStyle
    normal_style = ParagraphStyle(
        'TableCell',
        fontName='DejaVuSans',
        fontSize=9,
        leading=10,
        alignment=TA_LEFT,
        wordWrap='CJK'  # Включаем перенос слов
    )
    header_style = ParagraphStyle(
        'TableHeader',
        parent=normal_style,
        fontName='DejaVuSans-Bold' if 'DejaVuSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'DejaVuSans',
        alignment=TA_CENTER,
        textColor=colors.black
    )
    
    # Подготовка данных: преобразуем строки в Paragraph
    table_data = []
    # Заголовки
    header_pars = [Paragraph(h, header_style) for h in headers]
    table_data.append(header_pars)
    # Данные
    for row in data:
        row_pars = [Paragraph(cell, normal_style) for cell in row]
        table_data.append(row_pars)
    
    # Создаём таблицу
    col_count = len(headers)
    # Вычисляем ширину столбцов: равномерно распределяем доступную ширину
    col_width = available_width / col_count
    # Ограничиваем минимальную и максимальную ширину
    min_col_width = 20 * mm
    max_col_width = 80 * mm
    if col_width < min_col_width:
        col_width = min_col_width
    elif col_width > max_col_width:
        col_width = max_col_width
    
    table = Table(table_data, colWidths=[col_width] * col_count, repeatRows=1)
    
    # Стиль таблицы
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    return table

def markdown_to_elements(text, styles, page_width):
    """Преобразует Markdown-текст в список элементов reportlab."""
    elements = []
    lines = text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        
        # Таблица
        if line.startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            table_text = '\n'.join(table_lines)
            parsed = parse_markdown_table(table_text)
            if parsed:
                headers, data = parsed
                # Доступная ширина для таблицы: ширина страницы минус поля
                available_width = page_width - 20 * mm  # запас
                table = create_table(headers, data, available_width)
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
                            rightMargin=20*mm, leftMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    
    # Создаём стили с кириллическим шрифтом
    normal_style = ParagraphStyle(
        'NormalRu',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=10,
        leading=12,
        wordWrap='CJK'
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
    
    # Ширина страницы для таблиц
    page_width = A4[0] - 40*mm  # ширина A4 минус левое и правое поля
    
    elements.extend(markdown_to_elements(content, custom_styles, page_width))
    doc.build(elements)
    print(f"PDF создан: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: generate_pdf_final.py <входной_файл.md> <выходной_файл.pdf>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    create_pdf(content, output_file)