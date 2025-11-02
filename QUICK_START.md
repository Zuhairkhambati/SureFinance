# Quick Start Guide

Follow these steps to get the application running quickly:

## Prerequisites Check

Make sure you have:
- Python 3.8+ installed (`python --version`)
- Node.js 16+ installed (`node --version`)
- npm installed (`npm --version`)

## Quick Setup (Windows)

### Option 1: Using Batch Scripts (Easiest)

1. **Start Backend** (in one terminal):
   ```bash
   start-backend.bat
   ```
   Wait for "Application startup complete" message.

2. **Start Frontend** (in another terminal):
   ```bash
   start-frontend.bat
   ```

3. Open browser to `http://localhost:5173`

### Option 2: Manual Setup

#### Backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Testing the Application

1. Navigate to `http://localhost:5173` in your browser
2. Upload a PDF credit card statement
3. Click "Parse Statement"
4. View the extracted information

## Troubleshooting

**Backend won't start:**
- Make sure port 8000 is not in use
- Check that all dependencies are installed: `pip install -r requirements.txt`

**Frontend won't start:**
- Make sure port 5173 is not in use
- Try deleting `node_modules` and running `npm install` again

**Cannot connect to backend:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify the API endpoint: `http://localhost:8000/api/parse`

**PDF parsing fails:**
- Ensure the PDF is a valid credit card statement
- Check that the issuer is one of the supported ones
- Verify the PDF has extractable text (not just images)

## API Testing

You can also test the API directly using curl:

```bash
curl -X POST "http://localhost:8000/api/parse" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/statement.pdf"
```

Or using Python:

```python
import requests

with open('statement.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/parse',
        files={'file': f}
    )
    print(response.json())
```



