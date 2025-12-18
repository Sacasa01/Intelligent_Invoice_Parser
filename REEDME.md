# Intelligent_Invoice_Parser
Automated Invoice Data Extraction Tool built with Python and Streamlit. A Proof of Concept (PoC) demonstrating OCR and Regex-based parsing for enterprise document workflows.
# Smart Invoice Extractor (PoC)

## Project Overview
This tool is a **Proof of Concept (PoC)** designed to automate the extraction of key financial data from unstructured PDF invoices. 

It serves as a demonstration of **Python-based Automation**, **OCR**, and **Data Structuring**, simulating the backend logic required for Enterprise Resource Planning (ERP) integration.

## Technical Architecture
- **Core:** Python 3.10+
- **Frontend:** Streamlit (Rapid Prototyping)
- **OCR Engine:** `pdfplumber` (Text extraction)
- **Logic:** Regex-based parsing optimized for International Data Formats.
- **Scalability:** Designed to be easily replaced by Azure AI Document Intelligence for production environments.

## Features
1. **Universal PDF Ingestion:** Accepts standard invoice formats.
2. **Intelligent Parsing:** Extracts Vendor Name, Invoice Date, and Total Amount.
3. **Data Normalization:** Outputs strictly formatted JSON.
4. **CSV Export:** Generates international standard CSV files for data analysis.

## How to Run
```bash
pip install -r requirements.txt
streamlit run app.py
