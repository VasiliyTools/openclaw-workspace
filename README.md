# OpenClaw Workspace Tools

This repository contains only the utility scripts and tools used by the OpenClaw assistant (Василий). No personal data, user information, or agent personalities are stored here.

## Tools Included

### PDF Generation
- `generate_pdf_final.py` – Creates PDF from Markdown with proper Cyrillic font (DejaVuSans) and correctly formatted tables (word wrapping, width constraints).
- `generate_pdf_advanced.py` – Earlier version that renders tables via ReportLab.
- `generate_pdf_with_font.py` – Adds DejaVuSans font; tables as plain text.
- `generate_pdf_simple.py` – Basic version with default ReportLab fonts.
- `generate_pdf.py` – Initial experimental script.

### OCR / Document Text Extraction
- `document_processor_final.py` – Extracts text from PDF (native or scanned) and images using Tesseract OCR with Russian and English support.
- `document_processor.py` – Earlier version.

### Voice Utilities
- Speech-to-text: Vosk (`vosk_transcribe.py`, `vosk-model/`).
- Text-to-speech: Piper TTS (`piper_tts.py`).

### Web Server (static only)
- The `webserver/` directory contains the Flask application and templates for serving the tools dashboard and reports. (Note: static reports are not stored in the repo; they are generated and served from the live workspace.)

### Helper Scripts
- `check_economic_data.py` – Example script for fetching economic data.
- `task_manager.py`, `task_command.py` – Simple task management utilities.
- `transcribe.py` – Wrapper for Vosk transcription.
- Other small utilities for testing and setup.

## Installation

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

4. Install system-level dependencies (Debian/Ubuntu example):
   ```bash
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr tesseract-ocr-rus \
                           fonts-dejavu-core \
                           libglib2.0-0 libsm6 libxext6 libxrender1 \
                           poppler-utils
   ```

5. Test PDF generation:
   ```bash
   python3 generate_pdf_final.py <source.md> <output.pdf>
   ```

6. Test OCR:
   ```bash
   python3 document_processor_final.py <input.pdf_or_image> > extracted.txt
   ```

7. Run the web server (if needed):
   ```bash
   cd webserver
   python3 app.py
   ```

## Notes
- This repository contains only the tools; runtime data (reports, logs, memories) are stored separately in the live OpenClaw workspace and are not committed here.
- For any issues, check script output or logs.

---
*Maintained by OpenClaw assistant (Василий).*