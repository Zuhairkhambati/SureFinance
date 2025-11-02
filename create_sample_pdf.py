"""
Script to create a sample credit card statement PDF for testing
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
import os

def create_sample_statement():
    """Create a sample Chase credit card statement PDF"""
    
    # Create PDF
    filename = "sample_chase_statement.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a56db'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Header style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=10,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Normal style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#374151'),
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Calculate dates
    end_date = datetime.now().replace(day=1) - timedelta(days=1)
    start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    due_date = end_date + timedelta(days=25)
    
    # Title
    title = Paragraph("CHASE", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Account Information - using plain text to ensure extractability
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
    
    story.append(account_info_header := Paragraph("Account Summary", header_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(account_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Billing Cycle - use date formats that parser expects (MM/DD/YYYY)
    billing_text = f"Billing Cycle: {start_date.strftime('%m/%d/%Y')} through {end_date.strftime('%m/%d/%Y')}"
    billing_info = Paragraph(f"<b>{billing_text}</b>", normal_style)
    story.append(billing_info)
    story.append(Spacer(1, 0.2*inch))
    
    # Add payment due date text separately - use MM/DD/YYYY format
    due_date_text = Paragraph(f"Payment Due Date: {due_date.strftime('%m/%d/%Y')}", normal_style)
    story.append(due_date_text)
    story.append(Spacer(1, 0.1*inch))
    
    # Also add alternative formats for better parser matching
    statement_period = Paragraph(f"Statement Period: {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}", normal_style)
    story.append(statement_period)
    story.append(Spacer(1, 0.1*inch))
    
    # Transactions
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
    
    # Summary - ensure total balance is extractable
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
    
    # Footer - add transaction count
    story.append(Spacer(1, 0.2*inch))
    transaction_count_text = Paragraph("Total Transactions: 10", normal_style)
    story.append(transaction_count_text)
    story.append(Spacer(1, 0.2*inch))
    
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
    
    # Build PDF
    doc.build(story)
    print(f"✅ Sample PDF created: {filename}")
    print(f"📄 Location: {os.path.abspath(filename)}")
    return filename

if __name__ == "__main__":
    create_sample_statement()

