# How to Create Sample PDF for Testing

## Option 1: Using the Python Script (Recommended)

1. **Install reportlab** (if not already installed):
   ```bash
   pip install reportlab
   ```

2. **Run the script**:
   ```bash
   python create_sample_pdf.py
   ```

3. **The PDF will be created** as `sample_chase_statement.pdf` in the root directory.

## Option 2: Manual Creation

You can create your own PDF manually with the following information:

- **Issuer**: Chase (or any supported issuer)
- **Card Last 4 Digits**: 4532 (or any 4 digits)
- **Billing Cycle**: Any date range format
- **Payment Due Date**: Any date format
- **Total Balance**: Any amount with $ symbol

The parser will automatically detect the issuer and extract the information.

## Supported Formats

The parser supports statements from:
- Chase
- American Express
- Bank of America
- Citi
- Capital One

Just include the issuer name anywhere in the PDF for automatic detection.


