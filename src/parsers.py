"""
Document Parsers Module
Specialized parsers for different document types
"""

from typing import Dict, Optional
from .ocr_engine import ocr_engine
import logging

logger = logging.getLogger(__name__)


class InvoiceParser:
    """Parser for invoice documents"""
    
    def __init__(self):
        self.ocr = ocr_engine
    
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse invoice PDF and extract structured data.
        
        Args:
            file_path: Path to invoice PDF
            
        Returns:
            Dictionary with extracted fields
        """
        logger.info(f"Parsing invoice: {file_path}")
        
        # Extract raw text
        text = self.ocr.extract_text_from_pdf(file_path)
        
        # Extract structured data
        dates = self.ocr.extract_dates(text)
        amounts = self.ocr.extract_amounts(text)
        vendor = self.ocr.extract_vendor(text)
        
        # Build result
        result = {
            "document_type": "invoice",
            "vendor": vendor,
            "invoice_date": dates[0] if dates else None,
            "total_amount": amounts[-1] if amounts else "0.00",
            "detected_amounts": amounts,
            "detected_dates": dates,
            "confidence": self._calculate_confidence(dates, amounts),
            "raw_text_length": len(text)
        }
        
        logger.info(f"Invoice parsed: {result['vendor']}, Amount: {result['total_amount']}")
        return result
    
    
    def _calculate_confidence(self, dates: list, amounts: list) -> float:
        """Calculate extraction confidence score"""
        score = 0.5  # Base score
        
        if dates:
            score += 0.25
        if amounts:
            score += 0.25
        
        return min(score, 1.0)


class ReceiptParser:
    """Parser for receipt documents"""
    
    def __init__(self):
        self.ocr = ocr_engine
    
    
    def parse(self, file_path: str) -> Dict:
        """
        Parse receipt PDF and extract structured data.
        
        Args:
            file_path: Path to receipt PDF
            
        Returns:
            Dictionary with extracted fields
        """
        logger.info(f"Parsing receipt: {file_path}")
        
        text = self.ocr.extract_text_from_pdf(file_path)
        dates = self.ocr.extract_dates(text)
        amounts = self.ocr.extract_amounts(text)
        vendor = self.ocr.extract_vendor(text)
        
        result = {
            "document_type": "receipt",
            "merchant": vendor,
            "purchase_date": dates[0] if dates else None,
            "total": amounts[-1] if amounts else "0.00",
            "items_detected": len(amounts),
            "confidence": 0.8 if (dates and amounts) else 0.5
        }
        
        return result