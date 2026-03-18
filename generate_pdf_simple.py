#!/usr/bin/env python3
"""
Простой генератор PDF из Markdown.
"""

import sys
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

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
    elements = []
    elements.append(Paragraph("Отчёт Финансиста", styles['Title']))
    elements.append(Spacer(1, 0.25*inch))
    elements.extend(markdown_to_paragraphs(content, styles))
    doc.build(elements)
    print(f"PDF создан: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: generate_pdf_simple.py <входной_файл.md> <выходной_файл.pdf>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    create_pdf(content, output_file)