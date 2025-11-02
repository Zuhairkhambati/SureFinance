# 💳 Credit Card Statement Parser - AI-Powered Financial Analysis

A production-ready, full-stack application that extracts key information from credit card statement PDFs across 5 major credit card issuers. Features AI-powered confidence scoring, interactive analytics, and intelligent financial insights.

## ✨ Features

### Core Functionality
- **PDF Parsing**: Robust text extraction from credit card statement PDFs
- **Multi-Issuer Support**: Automatically detects and parses statements from:
  - Chase
  - American Express
  - Bank of America
  - Citi
  - Capital One
- **5 Key Data Points Extracted**:
  1. Card Last 4 Digits
  2. Billing Cycle (Start & End Dates)
  3. Payment Due Date
  4. Total Balance
  5. Transaction Information (Count & Total Charges)

### Advanced Features 🚀
- **AI-Powered Confidence Scoring**: Every extracted data point has a confidence score (0-100%)
- **Interactive Analytics Dashboard**: Beautiful charts and visualizations showing data quality
- **Intelligent Insights Engine**: AI-generated payment recommendations and spending analysis
- **Export Functionality**: Export to CSV or JSON format
- **Batch Processing**: Upload and parse multiple statements at once
- **Swagger API Documentation**: Interactive API docs at `/docs`
- **Modern UI**: Responsive design with smooth animations and professional styling
- **Metadata Tracking**: Extraction timestamps, PDF page counts, and text analysis

## Project Structure

```
SureFinance/
├── backend/           # FastAPI backend
│   ├── main.py       # API routes and server
│   ├── parsers.py    # PDF parsing logic for each issuer
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── App.tsx   # Main React component
│   │   └── ...
│   └── package.json
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

## Installation & Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the backend server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

The frontend will be available at `http://localhost:5173`

## Usage

1. Start both the backend and frontend servers (see Installation above)
2. Open your browser to `http://localhost:5173`
3. Click "Choose PDF Statement" and select a credit card statement PDF
4. Click "Parse Statement" to extract the information
5. View the extracted data points displayed in the results section

## API Endpoints

### POST `/api/parse`
Upload and parse a credit card statement PDF.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "detected_issuer": "Chase",
  "card_last_four_digits": "1234",
  "billing_cycle": {
    "start_date": "01/01/2024",
    "end_date": "01/31/2024"
  },
  "payment_due_date": "02/15/2024",
  "total_balance": "$1,234.56",
  "transaction_info": {
    "transaction_count": "25",
    "total_charges": "$987.65"
  }
}
```

### GET `/api/supported-issuers`
Get list of supported credit card issuers.

**Response:**
```json
{
  "supported_issuers": [
    "Chase",
    "American Express",
    "Bank of America",
    "Citi",
    "Capital One"
  ]
}
```

## How It Works

1. **PDF Text Extraction**: Uses `pdfplumber` to extract text content from uploaded PDFs
2. **Issuer Detection**: Analyzes the PDF text to identify which credit card issuer the statement is from
3. **Parsing**: Uses issuer-specific parsers with regex patterns to extract the 5 key data points
4. **Response**: Returns structured JSON with all extracted information

## Technical Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **pdfplumber**: PDF text extraction library
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Fast build tool and dev server
- **Axios**: HTTP client for API requests

## Notes

- The parser uses regex patterns to identify and extract data. For best results, use actual credit card statement PDFs from the supported issuers.
- If certain data points cannot be extracted, they will be marked as "N/A" in the results.
- The parser automatically detects the issuer based on keywords in the PDF text.

## Future Enhancements

- Support for more credit card issuers
- Batch processing of multiple statements
- Export extracted data to CSV/JSON
- Transaction line-item extraction
- Statement date validation
- OCR support for scanned PDFs

## License

This project is created for assignment purposes.

