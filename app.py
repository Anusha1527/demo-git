import os
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import cv2
import pytesseract
from google.cloud import vision
from PIL import Image
from reportlab.pdfgen import canvas
import re
from fuzzywuzzy import fuzz
from database import initialize_database, save_to_database, fetch_all_medicines

# Initialize Database
initialize_database()

# Handle Missing Google Cloud Credentials
if not os.path.exists("key.json"):
    st.error("❌ Google Cloud Vision API key not found. Please upload key.json.")
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

# Page Config
st.set_page_config(
    page_title="Medical Assistant",
    page_icon="🩺",
    layout="wide"
)

# Fetch Medicines from Database
medicines_from_db = fetch_all_medicines()
medicine_list = [med[1].lower() for med in medicines_from_db]  # Convert to lowercase

# 🔹 Function: Extract Medicines using Fuzzy Matching
def extract_medicines(text):
    detected_medicines = []
    words = text.lower().split()
    for med in medicine_list:
        for word in words:
            if fuzz.partial_ratio(med, word) > 80:
                detected_medicines.append(med)
    return ", ".join(set(detected_medicines)) if detected_medicines else "No medicines found"

# 🔹 Function: Extract Text using Google Vision API & Tesseract
def extract_text(image_bytes):
    # Use Google Vision API
    client = vision.ImageAnnotatorClient()
    vision_image = vision.Image(content=image_bytes)
    response = client.text_detection(image=vision_image)
    
    if response.text_annotations:
        raw_text = response.text_annotations[0].description
    else:
        raw_text = ""
    
    # Use Tesseract as a backup OCR method
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    processed_img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)[1]
    tesseract_text = pytesseract.image_to_string(processed_img)
    
    # Combine results
    final_text = raw_text if raw_text else tesseract_text
    detected_medicines = extract_medicines(final_text)
    return final_text, detected_medicines

# 🔹 Function: Generate PDF
def generate_pdf(text):
    pdf_path = "extracted_prescription.pdf"
    c = canvas.Canvas(pdf_path)
    c.setFont("Helvetica", 12)
    lines = text.split("\n")
    y_position = 800
    for line in lines:
        c.drawString(100, y_position, line)
        y_position -= 50  
    c.save()
    return pdf_path

# 📌 Prescription OCR Page
st.sidebar.markdown("## Contents ##")
page = st.sidebar.radio("Choose a page", ["🏠 Home", "📄 Prescription OCR", "💊 Medicine Matching"])

if page == "🏠 Home":
    st.title(" Welcome to Medical Assistant ")
    st.write("How can i help you ?")
    st.image(r"C:\Users\anush\Downloads\app.jpg", caption="Medical Assistant", use_container_width=True)

if page == "📄 Prescription OCR":
    st.markdown("## Prescription OCR 📄")
    uploaded_file = st.file_uploader("Upload a Prescription Image", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        image_bytes = uploaded_file.read()
        st.image(image_bytes, caption=" Uploaded Prescription ", use_container_width=True)

        extracted_text, extracted_medicines = extract_text(image_bytes)
        st.subheader("📌 Extracted Text")
        st.code(extracted_text, language="plaintext")
        st.subheader("💊 Detected Medicines")
        st.write(extracted_medicines)

        name = st.text_input("Enter Patient Name:")
        age = st.number_input("Enter Patient Age:", min_value=0, max_value=120, format="%d")
        
        if name.strip() and age:
            if st.button("Save to Database"):
                save_to_database(name, int(age), extracted_text, extracted_medicines)
                st.success("Patient details saved successfully! ✅")
        else:
            st.warning("⚠️ Please enter patient name and age before saving.")

        if extracted_text:
            pdf_path = generate_pdf(extracted_text)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(label="📥 Download Extracted Prescription",
                                   data=pdf_file,
                                   file_name="extracted_prescription.pdf",
                                   mime="application/pdf")
