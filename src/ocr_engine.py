"""
OCR Engine Module
Handles PDF text extraction using pdfplumber
"""

import pdfplumber
import re
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OCREngine:
    """PDF text extraction engine"""
    
    def __init__(self):
        logger.info("OCR Engine initialized")
    
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract raw text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            Exception: If PDF cannot be read
        """
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    
    def extract_dates(self, text: str) -> list:
        """
        Extract dates from text using regex patterns.
        Supports: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
        
        Args:
            text: Input text
            
        Returns:
            List of detected dates
        """
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',           # YYYY-MM-DD
            r'\d{2}[/-]\d{2}[/-]\d{2,4}'    # DD/MM/YYYY or DD-MM-YYYY
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return dates
    
    
    def extract_amounts(self, text: str) -> list:
        """
        Extract monetary amounts from text.
        Supports: 1,200.50 or 1200.50
        
        Args:
            text: Input text
            
        Returns:
            List of detected amounts
        """
        # Pattern: numbers with optional commas and mandatory decimals
        amount_pattern = r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b'
        amounts = re.findall(amount_pattern, text)
        
        return amounts
    
    
    def extract_vendor(self, text: str) -> str:
        """
        Heuristic: Extract vendor name (typically first line).
        
        Args:
            text: Input text
            
        Returns:
            Vendor name or "Unknown"
        """
        lines = text.strip().split('\n')
        if lines:
            vendor = lines[0].strip()
            # Clean up if too long
            if len(vendor) > 100:
                vendor = vendor[:100] + "..."
            return vendor
        return "Unknown Vendor"


# Singleton instance
ocr_engine = OCREngine()