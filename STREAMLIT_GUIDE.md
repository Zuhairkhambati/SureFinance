# Streamlit Deployment Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Locally

```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## Deploying to Streamlit Cloud

### Option 1: Deploy from GitHub

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository and branch
6. Set the main file path to: `streamlit_app.py`
7. Click "Deploy"

### Option 2: Using Streamlit CLI

```bash
streamlit login
streamlit deploy streamlit_app.py
```

## File Structure for Streamlit

Make sure your repository has:
```
SureFinance/
├── streamlit_app.py      # Main Streamlit application
├── requirements.txt      # Python dependencies
├── backend/
│   └── parsers.py        # Parser classes (required)
└── README.md
```

## Environment Variables

If you need environment variables, create a `.streamlit/secrets.toml` file (for local) or use Streamlit Cloud's secrets management.

## Requirements

The `requirements.txt` should include:
- streamlit>=1.28.0
- pdfplumber>=0.10.3
- reportlab>=4.0.7
- pypdf>=3.17.4

## Troubleshooting

### Import Errors
- Make sure `backend/parsers.py` is accessible
- The app adds `backend/` to the Python path automatically

### PDF Parsing Issues
- Ensure uploaded PDFs contain selectable text (not scanned images)
- Password-protected PDFs require the password input

### Memory Issues
- Streamlit Cloud has memory limits
- For large PDFs, consider processing in chunks

## Features

- ✅ PDF Upload & Parsing
- ✅ Password-protected PDF support
- ✅ Multi-bank detection (9+ Indian banks)
- ✅ Confidence scoring
- ✅ Analytics & recommendations
- ✅ CSV/JSON export
- ✅ Sample PDF generation

