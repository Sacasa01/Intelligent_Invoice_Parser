import streamlit as st
import pdfplumber
import pandas as pd
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Smart Invoice Extractor", layout="wide")

st.title("📄 Smart Invoice Extractor (PoC)")
st.markdown("""
**Automated Data Extraction Tool.** Upload unstructured PDF invoices to extract structured data via OCR.
*Tech Stack: Python, OCR, Regex. Ready for LLM integration.*
""")

# --- BACKEND LOGIC ---

def extract_text_from_pdf(file):
    """Extracts raw text from the uploaded PDF."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def analyze_invoice_data(text):
    """
    Analyzes text to find key fields using Regex patterns.
    Optimized for International formats (ISO Dates, Dot Decimals).
    """
    data = {}
    
    # 1. DATE DETECTION
    # Supports: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
    date_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}[/-]\d{2}[/-]\d{2,4})'
    dates = re.findall(date_pattern, text)
    
    # 2. AMOUNT DETECTION (International Format: 1,200.50)
    # Looks for numbers ending in .XX (standard currency format)
    amount_pattern = r'\b\d{1,3}(?:,\d{3})*\.\d{2}\b'
    amounts = re.findall(amount_pattern, text)

    # 3. VENDOR DETECTION (Heuristic: First line of text)
    data['vendor'] = text.split('\n')[0] if text else "Unknown Vendor"
    
    # 4. FIELD ASSIGNMENT
    data['invoice_date'] = dates[0] if dates else "Not detected"
    
    # Logic: The last amount found is usually the Total (bottom of the page)
    if amounts:
        data['total_amount'] = amounts[-1] 
    else:
        # Fallback for testing with simple numbers if strict format fails
        data['total_amount'] = "0.00"
    
    return data

# --- FRONTEND UI ---

st.sidebar.header("Upload System")
uploaded_file = st.sidebar.file_uploader("Drop PDF Invoice here", type=["pdf"])

if uploaded_file is not None:
    # 1. Processing
    with st.spinner('Scanning document...'):
        raw_text = extract_text_from_pdf(uploaded_file)
        extracted_data = analyze_invoice_data(raw_text)

    # 2. Display Results
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔍 OCR Raw Data")
        st.text_area("Extracted Text", raw_text, height=400)

    with col2:
        st.subheader("📊 Structured Output")
        st.success("Extraction Complete")
        st.json(extracted_data)
        
        # --- EXPORT SECTION ---
        df = pd.DataFrame([extracted_data])
        
        # NOTE: We use ',' separator for International Standard CSV.
        # If opening in Excel (EU/Spain), use 'Data > From Text/CSV' to import correctly.
        csv = df.to_csv(index=False, sep=',', encoding='utf-8')
        
        st.download_button(
            label="💾 Download CSV Report",
            data=csv,
            file_name='invoice_extract.csv',
            mime='text/csv',
        )

else:
    st.info("Waiting for file upload...")
    st.markdown("---")
    st.caption("Developed by [Your Name] - Open Source Portfolio Project")