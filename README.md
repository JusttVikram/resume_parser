# Resume Parser

A simple resume parser that extracts structured information from PDF, DOCX, and TXT resume files using rule-based extraction with OCR fallback for scanned documents.

## Features

- **Multi-format support**: PDF, DOCX, and TXT files
- **OCR capabilities**: Automatic fallback for scanned/image-based PDFs
- **Web interface**: Simple Streamlit frontend
- **Command-line interface**: Direct script execution
- **Clean JSON output**: Structured data ready for integration


## Setup Instructions

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd resume_parser
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR (for scanned PDFs)**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   ```

## How to Run

### Web Interface (Recommended)

Start the Streamlit app:
```bash
streamlit run app.py
```
Then open `http://localhost:8501` in your browser.

### Command Line
```bash
python main.py path/to/resume.pdf
```

## Extracted Information

- Personal Information (Name, Email, Phone, LinkedIn, Address)
- Professional Summary/Objective
- Skills, Work Experience, Education
- Certifications, Languages, Projects, Internships

## Libraries Used

| Library | Purpose |
|---------|---------|
| **streamlit** | Web interface |
| **pdfplumber** | PDF text extraction |
| **python-docx** | Word document processing |
| **pytesseract** | OCR for scanned documents |
| **pdf2image** | Convert PDF to images |
| **pillow** | Image processing |

## Project Structure

```
resume_parser/
├── main.py              # Core parsing logic
├── app.py               # Web interface
├── ocr.py               # OCR functionality
├── requirements.txt     # Dependencies
├── README.md           # This file
├── sample_resume/      # Test files
└── json_output/        # Generated JSON files
```
