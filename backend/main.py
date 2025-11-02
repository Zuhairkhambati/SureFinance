from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, List
import pdfplumber
import re
import io
import csv
import json
from datetime import datetime
from parsers import CreditCardParser, ChaseParser, AmexParser, BoAParser, CitiParser, CapitalOneParser

app = FastAPI(
    title="Credit Card Statement Parser API",
    description="Advanced PDF parser for extracting and analyzing credit card statement data across 5 major issuers",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map parsers to issuer names
PARSERS: Dict[str, CreditCardParser] = {
    "chase": ChaseParser(),
    "american express": AmexParser(),
    "amex": AmexParser(),
    "bank of america": BoAParser(),
    "boa": BoAParser(),
    "citi": CitiParser(),
    "citibank": CitiParser(),
    "capital one": CapitalOneParser(),
    "capitalone": CapitalOneParser(),
}


def detect_issuer(text: str) -> str:
    """Detect credit card issuer from PDF text"""
    text_lower = text.lower()
    
    # Check for issuer keywords
    if any(keyword in text_lower for keyword in ["chase", "jpmorgan", "jp morgan"]):
        return "chase"
    elif any(keyword in text_lower for keyword in ["american express", "amex", "americanexpress"]):
        return "amex"
    elif any(keyword in text_lower for keyword in ["bank of america", "bofa", "bankofamerica"]):
        return "boa"
    elif any(keyword in text_lower for keyword in ["citi", "citibank", "citigroup"]):
        return "citi"
    elif any(keyword in text_lower for keyword in ["capital one", "capitalone"]):
        return "capital one"
    
    return "unknown"


@app.get("/")
async def root():
    return {"message": "Credit Card Statement Parser API", "version": "1.0.0"}


@app.post("/api/parse")
async def parse_statement(file: UploadFile = File(...)):
    """Parse credit card statement PDF and extract key data points"""
    try:
        # Read PDF file
        contents = await file.read()
        
        # Extract text from PDF
        pdf_text = ""
        pdf_bytes = io.BytesIO(contents)
        with pdfplumber.open(pdf_bytes) as pdf_doc:
            for page in pdf_doc.pages:
                pdf_text += page.extract_text() or ""
        
        if not pdf_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Detect issuer
        issuer = detect_issuer(pdf_text)
        
        if issuer == "unknown":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Could not identify credit card issuer",
                    "supported_issuers": ["Chase", "American Express", "Bank of America", "Citi", "Capital One"]
                }
            )
        
        # Get appropriate parser
        parser = PARSERS.get(issuer)
        if not parser:
            raise HTTPException(status_code=400, detail=f"Parser not found for issuer: {issuer}")
        
        # Parse statement
        result = parser.parse(pdf_text, contents)
        result["detected_issuer"] = issuer.title()
        
        # Add confidence scores and metadata
        result["confidence_scores"] = calculate_confidence_scores(result)
        # Count pages for metadata
        with pdfplumber.open(io.BytesIO(contents)) as pdf_doc:
            page_count = len(pdf_doc.pages)
        result["extraction_metadata"] = {
            "extracted_at": datetime.now().isoformat(),
            "pdf_pages": page_count,
            "text_length": len(pdf_text)
        }
        result["analytics"] = generate_analytics(result)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error parsing PDF: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")


def calculate_confidence_scores(result: Dict[str, Any]) -> Dict[str, float]:
    """Calculate confidence scores for extracted data points"""
    scores = {}
    
    # Card digits confidence
    if result.get("card_last_four_digits") and result["card_last_four_digits"] != "N/A":
        scores["card_last_four_digits"] = 0.95
    else:
        scores["card_last_four_digits"] = 0.0
    
    # Billing cycle confidence
    if (result.get("billing_cycle") and 
        result["billing_cycle"].get("start_date") != "N/A" and
        result["billing_cycle"].get("end_date") != "N/A"):
        scores["billing_cycle"] = 0.90
    else:
        scores["billing_cycle"] = 0.0
    
    # Payment due date confidence
    if result.get("payment_due_date") and result["payment_due_date"] != "N/A":
        scores["payment_due_date"] = 0.90
    else:
        scores["payment_due_date"] = 0.0
    
    # Total balance confidence
    if result.get("total_balance") and result["total_balance"] != "N/A":
        scores["total_balance"] = 0.95
    else:
        scores["total_balance"] = 0.0
    
    # Transaction info confidence
    tx_info = result.get("transaction_info", {})
    if tx_info.get("transaction_count") != "N/A" or tx_info.get("total_charges") != "N/A":
        scores["transaction_info"] = 0.85
    else:
        scores["transaction_info"] = 0.0
    
    # Overall confidence
    scores["overall"] = sum(scores.values()) / len([v for k, v in scores.items() if k != "overall"])
    
    return scores


def generate_analytics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate analytics and insights from parsed data"""
    analytics = {
        "spending_insights": {},
        "payment_recommendations": [],
        "trends": {}
    }
    
    # Extract balance for insights
    balance_str = result.get("total_balance", "N/A")
    if balance_str != "N/A":
        try:
            balance = float(balance_str.replace("$", "").replace(",", ""))
            analytics["spending_insights"]["current_balance"] = balance
            
            # Add recommendations based on balance
            if balance > 5000:
                analytics["payment_recommendations"].append({
                    "type": "high_balance",
                    "message": "Consider making a larger payment to reduce interest charges",
                    "priority": "high"
                })
            elif balance > 2000:
                analytics["payment_recommendations"].append({
                    "type": "moderate_balance",
                    "message": "Consider paying more than the minimum to reduce debt faster",
                    "priority": "medium"
                })
            
            # Transaction insights
            tx_info = result.get("transaction_info", {})
            if tx_info.get("transaction_count") != "N/A":
                tx_count = int(tx_info["transaction_count"])
                if tx_count > 30:
                    analytics["payment_recommendations"].append({
                        "type": "high_transaction_count",
                        "message": f"You have {tx_count} transactions this period. Review your spending patterns.",
                        "priority": "medium"
                    })
        except:
            pass
    
    return analytics


@app.post("/api/parse/batch")
async def parse_batch(files: List[UploadFile] = File(...)):
    """Parse multiple credit card statements at once"""
    results = []
    errors = []
    
    for file in files:
        try:
            contents = await file.read()
            pdf_text = ""
            pdf_bytes = io.BytesIO(contents)
            with pdfplumber.open(pdf_bytes) as pdf_doc:
                for page in pdf_doc.pages:
                    pdf_text += page.extract_text() or ""
            
            if not pdf_text:
                errors.append({"filename": file.filename, "error": "Could not extract text"})
                continue
            
            issuer = detect_issuer(pdf_text)
            if issuer == "unknown":
                errors.append({"filename": file.filename, "error": "Unknown issuer"})
                continue
            
            parser = PARSERS.get(issuer)
            if parser:
                result = parser.parse(pdf_text, contents)
                result["detected_issuer"] = issuer.title()
                result["filename"] = file.filename
                result["confidence_scores"] = calculate_confidence_scores(result)
                results.append(result)
        except Exception as e:
            errors.append({"filename": file.filename, "error": str(e)})
    
    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@app.post("/api/export/csv")
async def export_to_csv(data: Dict[str, Any]):
    """Export parsed data to CSV format (Excel-compatible)"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write metadata header
    writer.writerow(["Credit Card Statement Data"])
    writer.writerow(["Extracted:", data.get("extraction_metadata", {}).get("extracted_at", datetime.now().isoformat())])
    writer.writerow([])  # Empty row
    
    # Write data in key-value format
    writer.writerow(["Field", "Value"])
    writer.writerow(["Issuer", data.get("detected_issuer", "N/A")])
    writer.writerow(["Card Last 4 Digits", data.get("card_last_four_digits", "N/A")])
    writer.writerow(["Payment Due Date", data.get("payment_due_date", "N/A")])
    writer.writerow(["Total Balance", data.get("total_balance", "N/A")])
    
    billing = data.get("billing_cycle", {})
    writer.writerow(["Billing Start", billing.get("start_date", "N/A")])
    writer.writerow(["Billing End", billing.get("end_date", "N/A")])
    
    tx_info = data.get("transaction_info", {})
    writer.writerow(["Transaction Count", tx_info.get("transaction_count", "N/A")])
    writer.writerow(["Total Charges", tx_info.get("total_charges", "N/A")])
    
    # Add confidence scores
    if data.get("confidence_scores"):
        writer.writerow([])  # Empty row
        writer.writerow(["Confidence Scores"])
        scores = data["confidence_scores"]
        for key, value in scores.items():
            if key != "overall":
                writer.writerow([key.replace("_", " ").title(), f"{value * 100:.1f}%"])
        writer.writerow(["Overall", f"{scores.get('overall', 0) * 100:.1f}%"])
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=statement_data.csv"}
    )


@app.get("/api/export/bank-details")
async def export_bank_details():
    """Download bank details reference file"""
    bank_data = """Issuer Name,Full Name,Official Website,Support Phone,Detection Keywords,Parser Class,Status
Chase,Chase Bank,https://www.chase.com,1-800-935-9935,chase;jpmorgan;jp morgan,ChaseParser,Active
American Express,American Express,https://www.americanexpress.com,1-800-528-4800,american express;amex;americanexpress,AmexParser,Active
Bank of America,Bank of America,https://www.bankofamerica.com,1-800-732-9194,bank of america;bofa;bankofamerica,BoAParser,Active
Citi,Citibank,https://www.citi.com,1-800-950-5114,citi;citibank;citigroup,CitiParser,Active
Capital One,Capital One,https://www.capitalone.com,1-800-955-7070,capital one;capitalone,CapitalOneParser,Active"""
    
    return StreamingResponse(
        io.BytesIO(bank_data.encode()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=bank_details.csv"}
    )


@app.post("/api/export/json")
async def export_to_json(data: Dict[str, Any]):
    """Export parsed data to JSON format"""
    json_str = json.dumps(data, indent=2)
    return StreamingResponse(
        io.BytesIO(json_str.encode()),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=statement_data.json"}
    )


@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics capabilities summary"""
    return {
        "features": [
            "Confidence scoring for all data points",
            "Spending insights and recommendations",
            "Payment recommendations based on balance",
            "Transaction pattern analysis",
            "Batch processing support",
            "CSV and JSON export"
        ]
    }


@app.get("/api/supported-issuers")
async def get_supported_issuers():
    """Get list of supported credit card issuers"""
    return {
        "supported_issuers": [
            "Chase",
            "American Express",
            "Bank of America",
            "Citi",
            "Capital One"
        ]
    }

