from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, List
import pdfplumber
import re
import io
import csv
import json
from datetime import datetime
from parsers import CreditCardParser, HDFCParser, ICICIParser, SBIParser, AxisParser, KotakParser, DCBParser, YesBankParser, IndusIndParser, OneCardParser

app = FastAPI(
    title="Credit Card Statement Parser API",
    description="Advanced PDF parser for extracting and analyzing credit card statement data across major Indian banks",
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
    "hdfc": HDFCParser(),
    "hdfc bank": HDFCParser(),
    "icici": ICICIParser(),
    "icici bank": ICICIParser(),
    "sbi": SBIParser(),
    "state bank of india": SBIParser(),
    "axis": AxisParser(),
    "axis bank": AxisParser(),
    "kotak": KotakParser(),
    "kotak mahindra": KotakParser(),
    "kotak mahindra bank": KotakParser(),
    "dcb": DCBParser(),
    "dcb bank": DCBParser(),
    "development credit bank": DCBParser(),
    "yes bank": YesBankParser(),
    "yes": YesBankParser(),
    "indusind": IndusIndParser(),
    "indusind bank": IndusIndParser(),
    "onecard": OneCardParser(),
    "one card": OneCardParser(),
}


def detect_issuer(text: str) -> str:
    """Detect credit card issuer from PDF text (Indian banks)"""
    text_lower = text.lower()
    
    # Check for issuer keywords (priority order matters - check full names first)
    # DCB Bank - check for "development credit" first to avoid false matches
    if "development credit bank" in text_lower or ("dcb bank" in text_lower and "dcb" in text_lower):
        return "dcb"
    elif "hdfc bank" in text_lower or ("hdfc" in text_lower and "housing development finance" not in text_lower):
        return "hdfc"
    elif "icici bank" in text_lower or "icici" in text_lower:
        return "icici"
    elif "state bank of india" in text_lower or ("sbi" in text_lower and "state" in text_lower):
        return "sbi"
    elif "axis bank" in text_lower or "axis" in text_lower:
        return "axis"
    elif "kotak mahindra bank" in text_lower or "kotak mahindra" in text_lower or "kotak" in text_lower:
        return "kotak"
    elif "yes bank" in text_lower:
        return "yes bank"
    elif "indusind bank" in text_lower or "indusind" in text_lower:
        return "indusind"
    elif "onecard" in text_lower or "one card" in text_lower:
        return "onecard"
    
    # Fallback: check individual keywords
    if "dcb" in text_lower:
        return "dcb"
    elif "hdfc" in text_lower:
        return "hdfc"
    elif "icici" in text_lower:
        return "icici"
    elif "sbi" in text_lower:
        return "sbi"
    elif "axis" in text_lower:
        return "axis"
    elif "kotak" in text_lower:
        return "kotak"
    elif "yes" in text_lower and "bank" in text_lower:
        return "yes bank"
    elif "indusind" in text_lower:
        return "indusind"
    elif "onecard" in text_lower or "one card" in text_lower:
        return "onecard"
    
    return "unknown"


@app.get("/")
async def root():
    return {"message": "Credit Card Statement Parser API", "version": "1.0.0"}


@app.post("/api/parse")
async def parse_statement(file: UploadFile = File(...), password: str = Form(None)):
    """Parse credit card statement PDF and extract key data points
    
    Args:
        file: The PDF file to parse
        password: Optional password for encrypted PDFs
    """
    try:
        # Read PDF file
        contents = await file.read()
        
        # Extract text from PDF
        pdf_text = ""
        pdf_bytes = io.BytesIO(contents)
        page_count = 0  # Initialize page count variable
        
        # Validate PDF file size
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="PDF file is empty")
        
        # Validate PDF header
        pdf_header = contents[:4]
        if pdf_header != b'%PDF':
            raise HTTPException(
                status_code=400, 
                detail="Invalid PDF file format. The file does not appear to be a valid PDF."
            )
        
        try:
            pdf_doc = None
            # First, try to open without password (if password not provided)
            # or with password (if provided)
            try:
                if password:
                    # Trim whitespace from password and reset BytesIO to beginning
                    password_trimmed = password.strip()
                    pdf_bytes.seek(0)
                    print(f"Attempting to open PDF with password (length: {len(password_trimmed)})")
                    pdf_doc = pdfplumber.open(pdf_bytes, password=password_trimmed)
                    print("PDF opened successfully with password")
                else:
                    # Try without password first
                    pdf_bytes.seek(0)
                    pdf_doc = pdfplumber.open(pdf_bytes)
            except Exception as open_error:
                error_type = type(open_error).__name__
                error_msg = str(open_error).lower()
                
                # Check if this is a password-related error
                is_password_error = (
                    "password" in error_msg or 
                    "encrypted" in error_msg or
                    "decrypt" in error_msg or
                    "file is encrypted" in error_msg or
                    error_type in ["FileNotDecryptedError", "PasswordError", "PdfReadError"] or
                    (hasattr(open_error, 'code') and "password" in str(open_error.code).lower())
                )
                
                if is_password_error:
                    if password:
                        # Password was provided but didn't work
                        print(f"Password error with provided password - Type: {error_type}, Message: {str(open_error)}")
                        raise HTTPException(
                            status_code=401, 
                            detail="Incorrect password. Please try again.",
                            headers={"X-Requires-Password": "true"}
                        )
                    else:
                        # No password provided, but one is needed
                        raise HTTPException(
                            status_code=401, 
                            detail="PDF is password-protected. Password required.",
                            headers={"X-Requires-Password": "true"}
                        )
                else:
                    # Not a password error, re-raise the original error
                    raise
            
            # If we got here, PDF opened successfully
            # Check number of pages and store the count for metadata
            page_count = len(pdf_doc.pages)
            if page_count == 0:
                pdf_doc.close()
                raise HTTPException(
                    status_code=400, 
                    detail="PDF has no pages or cannot be read."
                )
            
            # Try to extract text from all pages
            for page_num, page in enumerate(pdf_doc.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text + "\n"
                except Exception as page_error:
                    # Log but continue with other pages
                    error_detail = str(page_error) or type(page_error).__name__
                    print(f"Warning: Could not extract text from page {page_num}: {error_detail}")
                    continue
            
            pdf_doc.close()
            
        except HTTPException:
            # Re-raise HTTP exceptions (like password errors)
            raise
        except Exception as pdf_error:
            # Handle any other errors that occur after PDF is opened
            error_type = type(pdf_error).__name__
            error_msg = str(pdf_error) if pdf_error else "Unknown error occurred"
            
            print(f"PDF Error after opening - Type: {error_type}, Message: {error_msg}")
            
            # Close PDF if it was opened
            if pdf_doc:
                try:
                    pdf_doc.close()
                except:
                    pass
            
            if "corrupted" in error_msg.lower() or "invalid" in error_msg.lower():
                error_detail = "PDF appears to be corrupted or invalid. Please verify the file."
            else:
                error_detail = f"Error reading PDF ({error_type}): {error_msg}. The PDF might be corrupted, encrypted, or in an unsupported format."
            
            raise HTTPException(status_code=400, detail=error_detail)
        
        if not pdf_text or len(pdf_text.strip()) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract text from PDF. The PDF might be image-based (scanned) or encrypted. Please ensure the PDF contains selectable text."
            )
        
        # Detect issuer
        issuer = detect_issuer(pdf_text)
        
        if issuer == "unknown":
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Could not identify credit card issuer",
                    "supported_issuers": ["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank", "Kotak Mahindra Bank", "DCB Bank", "Yes Bank", "IndusInd Bank", "OneCard"]
                }
            )
        
        # Get appropriate parser
        parser = PARSERS.get(issuer)
        if not parser:
            raise HTTPException(status_code=400, detail=f"Parser not found for issuer: {issuer}")
        
        # Parse statement
        result = parser.parse(pdf_text, contents)
        # Handle special case for issuer names
        issuer_display_names = {
            "hdfc": "HDFC Bank",
            "icici": "ICICI Bank",
            "sbi": "State Bank of India",
            "axis": "Axis Bank",
            "kotak": "Kotak Mahindra Bank",
            "dcb": "DCB Bank",
            "yes bank": "Yes Bank",
            "indusind": "IndusInd Bank",
            "onecard": "OneCard"
        }
        result["detected_issuer"] = issuer_display_names.get(issuer, issuer.title())
        
        # Add confidence scores and metadata
        result["confidence_scores"] = calculate_confidence_scores(result)
        # Use the page count we already got when opening the PDF
        result["extraction_metadata"] = {
            "extracted_at": datetime.now().isoformat(),
            "pdf_pages": page_count,
            "text_length": len(pdf_text)
        }
        result["analytics"] = generate_analytics(result)
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are already properly formatted)
        raise
    except Exception as e:
        # Catch any unhandled exceptions and return proper error response
        import traceback
        error_trace = traceback.format_exc()
        error_type = type(e).__name__
        error_msg = str(e) if e else "Unknown error occurred"
        
        print(f"Unhandled Error parsing PDF - Type: {error_type}, Message: {error_msg}")
        print(f"Traceback: {error_trace}")
        
        # Check if it's a password-related error that we might have missed
        error_msg_lower = error_msg.lower()
        if "password" in error_msg_lower or "encrypted" in error_msg_lower or "decrypt" in error_msg_lower:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "PDF is password-protected. Password required or incorrect password provided.",
                    "error": error_msg
                },
                headers={"X-Requires-Password": "true"}
            )
        
        # Return detailed error for other cases
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Error parsing PDF: {error_msg}",
                "type": error_type,
                "detail": error_trace.split('\n')[-2] if len(error_trace.split('\n')) > 2 else str(e)
            }
        )


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
            # Remove currency symbols (₹ or $) and commas
            balance = float(balance_str.replace("₹", "").replace("$", "").replace(",", "").replace(" ", ""))
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
                # Handle special case for issuer names
                issuer_display_names = {
                    "hdfc": "HDFC Bank",
                    "icici": "ICICI Bank",
                    "sbi": "State Bank of India",
                    "axis": "Axis Bank",
                    "kotak": "Kotak Mahindra Bank",
                    "dcb": "DCB Bank",
                    "yes bank": "Yes Bank",
                    "indusind": "IndusInd Bank",
                    "onecard": "OneCard"
                }
                result["detected_issuer"] = issuer_display_names.get(issuer, issuer.title())
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
HDFC Bank,HDFC Bank Limited,https://www.hdfcbank.com,1800-202-6161,hdfc bank;hdfc,HDFCParser,Active
ICICI Bank,ICICI Bank Limited,https://www.icicibank.com,1800-1080,icici bank;icici,ICICIParser,Active
State Bank of India,State Bank of India,https://www.sbi.co.in,1800-11-2211,state bank of india;sbi,SBIParser,Active
Axis Bank,Axis Bank Limited,https://www.axisbank.com,1800-419-5577,axis bank;axis,AxisParser,Active
Kotak Mahindra Bank,Kotak Mahindra Bank,https://www.kotak.com,1800-266-1234,kotak mahindra bank;kotak,KotakParser,Active
DCB Bank,DCB Bank Limited,https://www.dcbbank.com,1800-209-5363,dcb bank;dcb;development credit bank,DCBParser,Active
Yes Bank,Yes Bank Limited,https://www.yesbank.in,1800-1200,yes bank;yes,YesBankParser,Active
IndusInd Bank,IndusInd Bank Limited,https://www.indusind.com,1800-2100,indusind bank;indusind,IndusIndParser,Active
OneCard,OneCard,https://www.getonecard.app,1800-2100,onecard;one card,OneCardParser,Active"""
    
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
            "HDFC Bank",
            "ICICI Bank",
            "State Bank of India",
            "Axis Bank",
            "Kotak Mahindra Bank",
            "DCB Bank",
            "Yes Bank",
            "IndusInd Bank"
        ]
    }


@app.post("/api/debug/pdf-info")
async def debug_pdf_info(file: UploadFile = File(...), password: str = Form(None)):
    """Debug endpoint to see PDF text extraction and bank detection"""
    try:
        contents = await file.read()
        pdf_text = ""
        pdf_bytes = io.BytesIO(contents)
        
        try:
            if password:
                pdf_doc = pdfplumber.open(pdf_bytes, password=password.strip())
            else:
                pdf_doc = pdfplumber.open(pdf_bytes)
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Failed to open PDF: {str(e)}"}
            )
        
        page_count = len(pdf_doc.pages)
        for i, page in enumerate(pdf_doc.pages):
            page_text = page.extract_text() or ""
            pdf_text += page_text + "\n"
        
        pdf_doc.close()
        
        # Get first 2000 characters for preview
        text_preview = pdf_text[:2000] if pdf_text else "No text extracted"
        text_preview_lines = text_preview.split('\n')[:50]  # First 50 lines
        
        # Try to detect issuer
        issuer = detect_issuer(pdf_text)
        
        # Find any bank-related keywords
        text_lower = pdf_text.lower()
        found_keywords = []
        all_keywords = [
            "hdfc", "icici", "sbi", "state bank", "axis", "kotak", "dcb", 
            "development credit", "yes bank", "indusind", "onecard", "one card"
        ]
        for keyword in all_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        # Test extraction methods
        from parsers import CreditCardParser
        test_parser = CreditCardParser.__subclasses__()[0]() if CreditCardParser.__subclasses__() else None
        
        extraction_results = {}
        if test_parser:
            extraction_results = {
                "card_last_four": test_parser.extract_last_four_digits(pdf_text),
                "billing_cycle": test_parser.extract_billing_cycle(pdf_text),
                "payment_due_date": test_parser.extract_payment_due_date(pdf_text),
                "total_balance": test_parser.extract_total_balance(pdf_text),
                "transaction_info": test_parser.extract_transaction_info(pdf_text)
            }
        
        return {
            "filename": file.filename,
            "pages": page_count,
            "text_length": len(pdf_text),
            "text_preview_lines": text_preview_lines,
            "text_preview": text_preview,
            "detected_issuer": issuer,
            "found_keywords": found_keywords,
            "has_text": len(pdf_text.strip()) > 0,
            "extraction_results": extraction_results
        }
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "detail": traceback.format_exc()}
        )

