from abc import ABC, abstractmethod
from typing import Dict, Any, List
import re
import pdfplumber
import io
from datetime import datetime


class CreditCardParser(ABC):
    """Base class for credit card statement parsers"""
    
    @abstractmethod
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        """Parse PDF text and extract key data points"""
        pass
    
    def extract_last_four_digits(self, text: str) -> str:
        """Extract card last 4 digits"""
        # Common patterns: ****1234, xxxx1234, ending in 1234
        patterns = [
            r'\*\*\*\*\s*(\d{4})',
            r'xxxx\s*(\d{4})',
            r'ending\s+in\s+(\d{4})',
            r'card\s+ending\s+(\d{4})',
            r'(\d{4})\s*ending',
            r'\b(\d{4})\s*(?:ending|expires)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Look for patterns like: 1234 5678 9012 3456
        card_pattern = r'\b\d{4}\s+\d{4}\s+\d{4}\s+(\d{4})\b'
        match = re.search(card_pattern, text)
        if match:
            return match.group(1)
        
        return "N/A"
    
    def extract_billing_cycle(self, text: str) -> Dict[str, str]:
        """Extract billing cycle start and end dates"""
        # Common patterns
        patterns = [
            r'billing\s+period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+to\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'statement\s+period[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+to\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+through\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "start_date": match.group(1),
                    "end_date": match.group(2)
                }
        
        return {"start_date": "N/A", "end_date": "N/A"}
    
    def extract_payment_due_date(self, text: str) -> str:
        """Extract payment due date"""
        patterns = [
            r'payment\s+due\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'due\s+date[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'minimum\s+payment\s+due\s+by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'pay\s+by[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "N/A"
    
    def extract_total_balance(self, text: str) -> str:
        """Extract total balance/amount due (supports both ₹ and $)"""
        patterns = [
            r'total\s+balance[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'new\s+balance[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'amount\s+due[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'total\s+amount\s+due[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'outstanding\s+amount[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'balance[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'₹\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return f"₹{float(amount):,.2f}"
        
        return "N/A"
    
    def extract_transaction_info(self, text: str) -> Dict[str, Any]:
        """Extract transaction summary"""
        # Try to find transaction count
        count_patterns = [
            r'(\d+)\s+transactions?',
            r'total\s+transactions?[:\s]+(\d+)',
        ]
        
        transaction_count = "N/A"
        for pattern in count_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                transaction_count = match.group(1)
                break
        
        # Try to extract total charges (supports both ₹ and $)
        charge_patterns = [
            r'total\s+charges[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'total\s+purchases[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'total\s+spend[:\s]+[₹$]?([\d,]+\.?\d*)',
            r'₹\s*([\d,]+\.?\d*)',
        ]
        
        total_charges = "N/A"
        for pattern in charge_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                total_charges = f"₹{float(amount):,.2f}"
                break
        
        return {
            "transaction_count": transaction_count,
            "total_charges": total_charges
        }


class HDFCParser(CreditCardParser):
    """Parser for HDFC Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "HDFC Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class ICICIParser(CreditCardParser):
    """Parser for ICICI Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "ICICI Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class SBIParser(CreditCardParser):
    """Parser for State Bank of India credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "State Bank of India",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class AxisParser(CreditCardParser):
    """Parser for Axis Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "Axis Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class KotakParser(CreditCardParser):
    """Parser for Kotak Mahindra Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "Kotak Mahindra Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class DCBParser(CreditCardParser):
    """Parser for DCB Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "DCB Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class YesBankParser(CreditCardParser):
    """Parser for Yes Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "Yes Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }


class IndusIndParser(CreditCardParser):
    """Parser for IndusInd Bank credit card statements"""
    
    def parse(self, text: str, pdf_bytes: bytes) -> Dict[str, Any]:
        return {
            "issuer": "IndusInd Bank",
            "card_last_four_digits": self.extract_last_four_digits(text),
            "billing_cycle": self.extract_billing_cycle(text),
            "payment_due_date": self.extract_payment_due_date(text),
            "total_balance": self.extract_total_balance(text),
            "transaction_info": self.extract_transaction_info(text)
        }



