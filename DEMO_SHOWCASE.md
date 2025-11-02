# 🎯 Quick Demo Showcase Guide

## Start the Application

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:5173`

## Quick Demo Checklist

### ✅ Feature Showcase (5 minutes)

1. **Upload Interface**
   - [ ] Show drag-and-drop styling
   - [ ] Upload a PDF statement
   - [ ] Point out file validation

2. **Extraction Results**
   - [ ] All 5 data points displayed
   - [ ] Confidence scores visible
   - [ ] Metadata shown (extraction time, pages)

3. **Analytics Tab**
   - [ ] Bar chart showing confidence distribution
   - [ ] Pie chart with data breakdown
   - [ ] Interactive tooltips

4. **Insights Tab**
   - [ ] AI recommendations displayed
   - [ ] Priority badges (High/Medium)
   - [ ] Spending insights

5. **Export Features**
   - [ ] CSV export (downloads file)
   - [ ] JSON export (downloads file)

6. **API Documentation**
   - [ ] Navigate to `http://localhost:8000/docs`
   - [ ] Show interactive Swagger UI
   - [ ] Test API endpoint directly

## Key Talking Points

- "The system automatically detects the credit card issuer from the PDF content"
- "Every data point has a confidence score to indicate extraction reliability"
- "The analytics dashboard provides visual insights into data quality"
- "AI-powered recommendations help users understand their spending patterns"
- "Export functionality enables integration with other financial tools"

## Impressive Features to Highlight

1. **Confidence Scoring**: Industry-standard approach to data quality
2. **Interactive Charts**: Professional data visualization
3. **AI Insights**: Goes beyond extraction to provide value
4. **Export Options**: Enterprise-ready functionality
5. **Beautiful UI**: Modern, responsive design
6. **Swagger Docs**: Professional API documentation

## Expected Questions & Answers

**Q: How does confidence scoring work?**
A: The system calculates confidence based on pattern match quality, data presence, and validation. Scores range from 0-100% for each extracted field.

**Q: Can you add more issuers?**
A: Yes, the modular parser architecture makes it easy. Just create a new parser class inheriting from the base parser.

**Q: How accurate is the extraction?**
A: The confidence scores indicate reliability. Higher scores mean more reliable extraction. The system uses multiple regex patterns with fallbacks.

**Q: Can this handle scanned PDFs?**
A: Currently optimized for text-based PDFs. OCR integration could be added for scanned documents.

**Q: How does batch processing work?**
A: The `/api/parse/batch` endpoint accepts multiple files and processes them sequentially, returning results and errors for each.



