# OpenClaw Workspace Tools

This repository contains the workspace and tools for the OpenClaw assistant (Василий). It includes scripts for PDF generation, OCR, document processing, voice commands, web server, and more.

## PDF Tools

### Purpose
Generate PDF files from Markdown sources with proper Cyrillic font support and correctly rendered tables (including word wrapping inside cells and width constraints).

### Scripts
- `generate_pdf_final.py` – Main script used to produce the latest financier report. It:
  * Registers DejaVuSans font (supports Russian/English).
  * Parses Markdown tables and converts them to ReportLab `Table` objects.
  * Calculates column widths to fit page, enables word wrapping inside cells.
  * Applies styles for headings, normal text, and lists.
- `generate_pdf_advanced.py` – Earlier version that renders tables via ReportLab but without fine width/word-wrap control.
- `generate_pdf_with_font.py` – Adds DejaVuSans font; tables drawn as plain text.
- `generate_pdf_simple.py` – Basic version using ReportLab's default fonts (no Cyrillic).
- `generate_pdf.py` – Initial experimental script.

### Usage
```bash
python3 generate_pdf_final.py source.md output.pdf
```
Replace `source.md` with your Markdown file and `output.pdf` with desired output path.

### Dependencies
Install via pip (already present in the environment):
```
reportlab
```
The DejaVuSans font files are expected at:
- `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`
- `/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`

If missing, install the package `fonts-dejavu-core` (Debian/Ubuntu) or equivalent.

## OCR / Document Processing

### Purpose
Extract text from PDF files (including scanned) and images using OCR with Russian and English language support.

### Main Script
- `document_processor_final.py` – Provides a command-line interface:
  * For native PDFs: uses `pdfplumber` or `PyMuPDF` to extract text.
  * For scanned PDFs or image files (JPG, PNG, etc.): applies preprocessing (grayscale, thresholding) then runs Tesseract OCR via `pytesseract`.
  * Outputs plain text to stdout (or can be redirected to a file).

### Usage
```bash
python3 document_processor_final.py input.pdf_or_image > extracted.txt
```
Supports single file input; for batch processing, wrap in a shell loop.

### Dependencies
- `pdfplumber`
- `pymupdf` (Fitz)
- `pytesseract`
- `Pillow`
- `opencv-python` (for image preprocessing)
- Tesseract OCR engine installed on the system with `rus` and `eng` language data:
  ```bash
  sudo apt-get install tesseract-ocr tesseract-ocr-rus
  ```
- Install Python packages via `pip install -r requirements.txt` (see below).

## Voice Tools

### Speech-to-text (STT)
- Uses Vosk API for offline speech recognition.
- Model: `vosk-model/` directory contains a small Russian-language model (download separately if needed).
- Script: `vosk_transcribe.py` – captures audio from microphone, transcribes to text in real time or from file.
- Additional helper: `transcribe.py` – simple wrapper for file-based transcription.

### Text-to-speech (TTS)
- Uses Piper TTS for high-quality offline synthesis.
- Script: `piper_tts.py` – converts text to speech using a selected voice (default Russian voice if available).
- Requires Piper binary and voice model files (can be installed via `pip install piper-tts` and downloading voices).

Both tools are integrated into the assistant for voice commands and audio responses.

## Web Server

- Flask app (`webserver/app.py`) providing:
  * Login protected dashboard.
  * Pages to view logs, system structure, financier reports, and list of reports.
  * Serves static files from `webserver/static/`.

## Memory & State

- Session logs: `memory/YYYY-MM-DD.md` (daily notes).
- Long-term memory: `MEMORY.md` (loaded only in main sessions).
- Identity, user, soul, tools descriptions in respective `.md` files.

## Setup / Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/VasiliyTools/openclaw-workspace.git
   cd openclaw-workspace
   ```
2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure system-level dependencies:
   ```bash
   # Debian/Ubuntu example
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr tesseract-ocr-rus \
                           fonts-dejavu-core \
                           libglib2.0-0 libsm6 libxext6 libxrender1 \
                           poppler-utils  # if using pdf2image elsewhere
   ```
5. Test PDF generation:
   ```bash
   python3 generate_pdf_final.py financier_reports.md test_output.pdf
   ```
6. Test OCR:
   ```bash
   python3 document_processor_final.py some_scanned.pdf > text.txt
   ```
7. Run the web server:
   ```bash
   cd webserver
   python3 app.py
   ```
   Then visit `http://localhost:8080` and log in with credentials shown at startup (default: `vasiliy` / `vasiliy123`).

## Notes
- The repository is updated automatically from the OpenClaw workspace via pushes from the assistant.
- All paths are relative to the workspace root.
- For any issues, consult the console output or logs.

---
*Maintained by OpenClaw assistant (Василий).*