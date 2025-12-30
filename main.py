"""
Document Intelligence API
FastAPI-based REST API for document processing and data extraction
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import uvicorn
import logging
import tempfile
import os
from pathlib import Path

from src.parsers import InvoiceParser, ReceiptParser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Document Intelligence API",
    description="OCR-based data extraction from unstructured documents (invoices, receipts, forms)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize parsers
invoice_parser = InvoiceParser()
receipt_parser = ReceiptParser()


# Response models
class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


class ExtractionResponse(BaseModel):
    status: str
    data: Dict
    confidence: float


# Root endpoint
@app.get("/", tags=["General"])
def root():
    """API root endpoint"""
    return {
        "message": "Document Intelligence API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "extract_invoice": "/api/v1/extract/invoice",
            "extract_receipt": "/api/v1/extract/receipt"
        }
    }


# Health check
@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """
    Health check endpoint for monitoring.
    Returns API status and version.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="Document Intelligence API is running"
    )


# Invoice extraction endpoint
@app.post("/api/v1/extract/invoice", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_invoice(file: UploadFile = File(...)):
    """
    Extract structured data from invoice PDFs.
    
    **Extracted Fields:**
    - Vendor name
    - Invoice date
    - Total amount
    - All detected amounts and dates
    
    **Supported Formats:**
    - PDF files only
    
    **Returns:**
    - JSON with extracted data and confidence score
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    logger.info(f"Processing invoice: {file.filename}")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Parse invoice
        result = invoice_parser.parse(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        return ExtractionResponse(
            status="success",
            data=result,
            confidence=result.get('confidence', 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error processing invoice: {e}")
        # Clean up temp file on error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# Receipt extraction endpoint
@app.post("/api/v1/extract/receipt", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_receipt(file: UploadFile = File(...)):
    """
    Extract structured data from receipt PDFs.
    
    **Extracted Fields:**
    - Merchant name
    - Purchase date
    - Total amount
    - Number of items
    
    **Supported Formats:**
    - PDF files only
    
    **Returns:**
    - JSON with extracted data and confidence score
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    logger.info(f"Processing receipt: {file.filename}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        result = receipt_parser.parse(tmp_path)
        os.unlink(tmp_path)
        
        return ExtractionResponse(
            status="success",
            data=result,
            confidence=result.get('confidence', 0.0)
        )
        
    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


# Batch processing endpoint (bonus)
@app.post("/api/v1/extract/batch", tags=["Extraction"])
async def extract_batch(files: list[UploadFile] = File(...)):
    """
    Process multiple documents in batch.
    
    **Note:** Limited to 10 files per request.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
    
    results = []
    for file in files:
        try:
            # Determine document type from filename
            if 'invoice' in file.filename.lower():
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    content = await file.read()
                    tmp.write(content)
                    result = invoice_parser.parse(tmp.name)
                    os.unlink(tmp.name)
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    content = await file.read()
                    tmp.write(content)
                    result = receipt_parser.parse(tmp.name)
                    os.unlink(tmp.name)
            
            results.append({
                "filename": file.filename,
                "status": "success",
                "data": result
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    return {"results": results, "total": len(files)}


# Run server (for local development)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )