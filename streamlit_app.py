"""
SureFinance - Credit Card Statement Parser & Generator
A Streamlit app for parsing and generating credit card statements
"""
import streamlit as st
import pdfplumber
import io
import re
import json
import csv
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import os

# Add backend directory to path to import parsers
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from parsers import (
    CreditCardParser, HDFCParser, ICICIParser, SBIParser, 
    AxisParser, KotakParser, DCBParser, YesBankParser, 
    IndusIndParser, OneCardParser
)

# Import PDF generation from reportlab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Configure Streamlit page
st.set_page_config(
    page_title="SureFinance - Credit Card Statement Parser",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'parsed_data' not in st.session_state:
    st.session_state.parsed_data = None
if 'parsed_filename' not in st.session_state:
    st.session_state.parsed_filename = None

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

SUPPORTED_BANKS = [
    "HDFC Bank",
    "ICICI Bank",
    "State Bank of India",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "DCB Bank",
    "Yes Bank",
    "IndusInd Bank",
    "OneCard"
]


def detect_issuer(text: str) -> str:
    """Detect credit card issuer from PDF text"""
    text_lower = text.lower()
    
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
    
    return "unknown"


def calculate_confidence_scores(result: Dict[str, Any]) -> Dict[str, float]:
    """Calculate confidence scores for extracted data points"""
    scores = {}
    
    if result.get("card_last_four_digits") and result["card_last_four_digits"] != "N/A":
        scores["card_last_four_digits"] = 0.95
    else:
        scores["card_last_four_digits"] = 0.0
    
    if (result.get("billing_cycle") and 
        result["billing_cycle"].get("start_date") != "N/A" and
        result["billing_cycle"].get("end_date") != "N/A"):
        scores["billing_cycle"] = 0.90
    else:
        scores["billing_cycle"] = 0.0
    
    if result.get("payment_due_date") and result["payment_due_date"] != "N/A":
        scores["payment_due_date"] = 0.90
    else:
        scores["payment_due_date"] = 0.0
    
    if result.get("total_balance") and result["total_balance"] != "N/A":
        scores["total_balance"] = 0.95
    else:
        scores["total_balance"] = 0.0
    
    tx_info = result.get("transaction_info", {})
    if tx_info.get("transaction_count") != "N/A" or tx_info.get("total_charges") != "N/A":
        scores["transaction_info"] = 0.85
    else:
        scores["transaction_info"] = 0.0
    
    non_overall_scores = [v for k, v in scores.items() if k != "overall"]
    scores["overall"] = sum(non_overall_scores) / len(non_overall_scores) if non_overall_scores else 0.0
    
    return scores


def generate_analytics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Generate analytics and insights from parsed data"""
    analytics = {
        "spending_insights": {},
        "payment_recommendations": [],
        "trends": {}
    }
    
    balance_str = result.get("total_balance", "N/A")
    if balance_str != "N/A":
        try:
            balance = float(balance_str.replace("₹", "").replace("$", "").replace(",", "").replace(" ", ""))
            analytics["spending_insights"]["current_balance"] = balance
            
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


def parse_pdf(file_bytes: bytes, password: str = None) -> Dict[str, Any]:
    """Parse PDF and extract credit card statement data"""
    pdf_text = ""
    pdf_bytes = io.BytesIO(file_bytes)
    
    try:
        if password:
            pdf_doc = pdfplumber.open(pdf_bytes, password=password.strip())
        else:
            pdf_doc = pdfplumber.open(pdf_bytes)
        
        for page in pdf_doc.pages:
            page_text = page.extract_text()
            if page_text:
                pdf_text += page_text + "\n"
        
        pdf_doc.close()
        
        if not pdf_text or len(pdf_text.strip()) == 0:
            raise ValueError("Could not extract text from PDF. The PDF might be image-based (scanned) or encrypted.")
        
        # Detect issuer
        issuer = detect_issuer(pdf_text)
        
        if issuer == "unknown":
            raise ValueError(f"Could not identify credit card issuer. Supported issuers: {', '.join(SUPPORTED_BANKS)}")
        
        # Get appropriate parser
        parser = PARSERS.get(issuer)
        if not parser:
            raise ValueError(f"Parser not found for issuer: {issuer}")
        
        # Parse statement
        result = parser.parse(pdf_text, file_bytes)
        
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
        result["confidence_scores"] = calculate_confidence_scores(result)
        result["extraction_metadata"] = {
            "extracted_at": datetime.now().isoformat(),
            "text_length": len(pdf_text)
        }
        result["analytics"] = generate_analytics(result)
        
        return result
        
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")


def create_sample_statement() -> bytes:
    """Create a sample credit card statement PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=10,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    end_date = datetime.now().replace(day=1) - timedelta(days=1)
    start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    due_date = end_date + timedelta(days=25)
    
    title = Paragraph("CHASE", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    account_info_data = [
        ['Account Number:', '**** **** **** 4532'],
        ['Statement Period:', f'{start_date.strftime("%m/%d/%Y")} - {end_date.strftime("%m/%d/%Y")}'],
        ['Payment Due Date:', due_date.strftime("%m/%d/%Y")],
        ['Total Balance:', '$2,456.78'],
        ['Card ending in:', '4532'],
    ]
    
    account_table = Table(account_info_data, colWidths=[2*inch, 3*inch])
    account_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
    ]))
    
    story.append(Paragraph("Account Summary", header_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(account_table)
    story.append(Spacer(1, 0.3*inch))
    
    billing_text = f"Billing Cycle: {start_date.strftime('%m/%d/%Y')} through {end_date.strftime('%m/%d/%Y')}"
    billing_info = Paragraph(f"<b>{billing_text}</b>", normal_style)
    story.append(billing_info)
    story.append(Spacer(1, 0.2*inch))
    
    due_date_text = Paragraph(f"Payment Due Date: {due_date.strftime('%m/%d/%Y')}", normal_style)
    story.append(due_date_text)
    story.append(Spacer(1, 0.1*inch))
    
    statement_period = Paragraph(f"Statement Period: {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}", normal_style)
    story.append(statement_period)
    story.append(Spacer(1, 0.1*inch))
    
    transactions = [
        ['Date', 'Description', 'Amount'],
        ['01/05/2024', 'AMAZON.COM PURCHASE', '$89.99'],
        ['01/08/2024', 'STARBUCKS COFFEE', '$12.50'],
        ['01/12/2024', 'NETFLIX SUBSCRIPTION', '$15.99'],
        ['01/15/2024', 'SHELL GAS STATION', '$45.23'],
        ['01/18/2024', 'WALMART PURCHASE', '$156.78'],
        ['01/22/2024', 'UBER RIDE', '$23.45'],
        ['01/25/2024', 'TARGET STORE', '$234.56'],
        ['01/28/2024', 'APPLE STORE', '$1,299.00'],
        ['01/30/2024', 'DOORDASH FOOD', '$67.89'],
        ['01/31/2024', 'WALGREENS PHARMACY', '$45.99'],
    ]
    
    transaction_table = Table(transactions, colWidths=[1.2*inch, 3.5*inch, 1.3*inch])
    transaction_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    
    story.append(Paragraph("Recent Transactions", header_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(transaction_table)
    story.append(Spacer(1, 0.3*inch))
    
    summary_data = [
        ['Previous Balance:', '$1,234.56'],
        ['Payments & Credits:', '-$500.00'],
        ['Purchases:', '+$1,992.28'],
        ['Total Charges:', '$1,992.28'],
        ['Fees Charged:', '$0.00'],
        ['Interest Charged:', '$0.00'],
        ['', ''],
        ['Total Balance:', '$2,456.78'],
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 6), (-1, 6), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#e5e7eb')),
        ('LINEABOVE', (0, 6), (-1, 6), 2, colors.HexColor('#1f2937')),
    ]))
    
    story.append(Paragraph("Statement Summary", header_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(summary_table)
    
    story.append(Spacer(1, 0.2*inch))
    transaction_count_text = Paragraph("Total Transactions: 10", normal_style)
    story.append(transaction_count_text)
    
    footer = Paragraph(
        "<i>This is a sample statement for testing purposes. Card ending in 4532.</i>",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )
    )
    story.append(footer)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def export_to_csv(data: Dict[str, Any]) -> str:
    """Export parsed data to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Credit Card Statement Data"])
    writer.writerow(["Extracted:", data.get("extraction_metadata", {}).get("extracted_at", datetime.now().isoformat())])
    writer.writerow([])
    
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
    
    if data.get("confidence_scores"):
        writer.writerow([])
        writer.writerow(["Confidence Scores"])
        scores = data["confidence_scores"]
        for key, value in scores.items():
            if key != "overall":
                writer.writerow([key.replace("_", " ").title(), f"{value * 100:.1f}%"])
        writer.writerow(["Overall", f"{scores.get('overall', 0) * 100:.1f}%"])
    
    return output.getvalue()


# Main App
st.title("💳 SureFinance - Credit Card Statement Parser")
st.markdown("### Parse, Analyze, and Generate Credit Card Statements")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a feature:", ["📄 Parse Statement", "📝 Generate Sample PDF", "ℹ️ About"])
    
    st.markdown("---")
    st.header("Supported Banks")
    for bank in SUPPORTED_BANKS:
        st.markdown(f"✓ {bank}")

# Main Content
if page == "📄 Parse Statement":
    st.header("Upload and Parse Credit Card Statement")
    st.markdown("Upload a PDF credit card statement to extract key information automatically.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"], help="Upload a credit card statement PDF")
    password = st.text_input("PDF Password (if protected)", type="password", help="Leave empty if PDF is not password protected")
    
    if uploaded_file is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        if st.button("🔍 Parse Statement", type="primary", use_container_width=True):
            with st.spinner("Parsing PDF... Please wait."):
                try:
                    file_bytes = uploaded_file.read()
                    
                    # Validate PDF
                    if len(file_bytes) == 0:
                        st.error("PDF file is empty")
                    elif file_bytes[:4] != b'%PDF':
                        st.error("Invalid PDF file format")
                    else:
                        result = parse_pdf(file_bytes, password if password else None)
                        st.session_state.parsed_data = result
                        st.session_state.parsed_filename = uploaded_file.name
                        st.success("✅ Statement parsed successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display parsed results
    if st.session_state.parsed_data:
        st.markdown("---")
        st.header("📊 Parsed Statement Data")
        
        data = st.session_state.parsed_data
        
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Issuer", data.get("detected_issuer", "N/A"))
        with col2:
            st.metric("Card Last 4 Digits", data.get("card_last_four_digits", "N/A"))
        with col3:
            st.metric("Total Balance", data.get("total_balance", "N/A"))
        with col4:
            st.metric("Payment Due Date", data.get("payment_due_date", "N/A"))
        
        # Detailed Information
        st.subheader("Account Details")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Billing Cycle:**\n\nStart: {data.get('billing_cycle', {}).get('start_date', 'N/A')}\n\nEnd: {data.get('billing_cycle', {}).get('end_date', 'N/A')}")
        
        with col2:
            tx_info = data.get("transaction_info", {})
            st.info(f"**Transaction Summary:**\n\nCount: {tx_info.get('transaction_count', 'N/A')}\n\nTotal Charges: {tx_info.get('total_charges', 'N/A')}")
        
        # Confidence Scores
        st.subheader("Confidence Scores")
        scores = data.get("confidence_scores", {})
        score_cols = st.columns(len([k for k in scores.keys() if k != "overall"]) + 1)
        idx = 0
        for key, value in scores.items():
            if key != "overall":
                with score_cols[idx]:
                    st.progress(value, text=f"{key.replace('_', ' ').title()}: {value*100:.1f}%")
                idx += 1
        with score_cols[-1]:
            overall = scores.get("overall", 0)
            st.metric("Overall Confidence", f"{overall*100:.1f}%")
        
        # Analytics
        analytics = data.get("analytics", {})
        if analytics.get("payment_recommendations"):
            st.subheader("💡 Recommendations")
            for rec in analytics["payment_recommendations"]:
                priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec.get("priority", "low"), "🔵")
                st.warning(f"{priority_color} {rec.get('message', '')}")
        
        # Export Options
        st.subheader("Export Data")
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            csv_data = export_to_csv(data)
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"statement_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with export_col2:
            json_data = json.dumps(data, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_data,
                file_name=f"statement_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Raw Data (expandable)
        with st.expander("🔍 View Raw Data"):
            st.json(data)

elif page == "📝 Generate Sample PDF":
    st.header("Generate Sample Credit Card Statement")
    st.markdown("Create a sample PDF credit card statement for testing purposes.")
    
    if st.button("🔄 Generate Sample PDF", type="primary"):
        with st.spinner("Generating PDF..."):
            try:
                pdf_bytes = create_sample_statement()
                st.success("✅ Sample PDF generated successfully!")
                
                st.download_button(
                    label="📥 Download Sample PDF",
                    data=pdf_bytes,
                    file_name="sample_chase_statement.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.info("💡 This sample PDF can be used to test the parser. It contains typical credit card statement information.")
            except Exception as e:
                st.error(f"❌ Error generating PDF: {str(e)}")

elif page == "ℹ️ About":
    st.header("About SureFinance")
    st.markdown("""
    ### Credit Card Statement Parser & Generator
    
    **SureFinance** is a powerful tool for parsing and analyzing credit card statements from major Indian banks.
    
    #### Features:
    - 🔍 **Automatic PDF Parsing**: Extract key information from credit card statements
    - 🏦 **Multi-Bank Support**: Works with 9+ major Indian banks
    - 📊 **Analytics & Insights**: Get spending insights and payment recommendations
    - 📥 **Export Options**: Download parsed data as CSV or JSON
    - 📝 **Sample Generation**: Generate test PDFs for development
    
    #### Supported Banks:
    """)
    for bank in SUPPORTED_BANKS:
        st.markdown(f"- {bank}")
    
    st.markdown("""
    #### How to Use:
    1. Navigate to **Parse Statement** tab
    2. Upload your credit card statement PDF
    3. Enter password if PDF is protected
    4. Click "Parse Statement" to extract data
    5. View results and download if needed
    
    #### Technology Stack:
    - **Streamlit** for the web interface
    - **PDFPlumber** for PDF text extraction
    - **ReportLab** for PDF generation
    - **Python** for parsing logic
    
    ---
    **Version:** 2.0.0
    """)

