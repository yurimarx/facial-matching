import streamlit as st
import requests

# API Configuration
API_URL = "http://facial-matching-api:5000/api"

st.set_page_config(page_title="IRIS Face Recognition", layout="wide")

st.title("👤 Facial Recognition System")

# Using tabs
tab1, tab2 = st.tabs(["Register User", "Search / Verify"])

# --- TAB 1: REGISTRATION ---
with tab1:
    st.header("New User Registration")
    
    # 1. Identity Data
    reg_name = st.text_input("Full Name", key="input_name")
    reg_ssn = st.text_input("SSN / ID Number", key="input_ssn")
    
    # 2. Source Toggle
    reg_source = st.radio("Select Image Source:", ["Camera", "Upload File"], 
                          horizontal=True, key="reg_src_toggle")
    
    reg_img = None
    if reg_source == "Camera":
        # Unique key for registration camera
        reg_img = st.camera_input("Take a registration photo", key="reg_cam_widget")
    else:
        # Unique key for registration uploader
        reg_img = st.file_uploader("Choose a photo", type=['jpg', 'jpeg', 'png'], key="reg_file_widget")

    # 3. Action Button
    if st.button("Finalize Registration", type="primary", key="btn_reg"):
        if not reg_name or not reg_ssn:
            st.warning("⚠️ Please provide Name and SSN.")
        elif reg_img is None:
            st.error("⚠️ No image detected. Please capture a photo or upload a file first.")
        else:
            # Get the bytes from the uploaded file or camera
            img_bytes = reg_img.getvalue()
            files = {'image': ('register.jpg', img_bytes, 'image/jpeg')}
            payload = {'name': reg_name, 'ssn': reg_ssn}
            
            with st.spinner("Communicating with Flask API..."):
                try:
                    res = requests.post(f"{API_URL}/register", files=files, data=payload)
                    if res.status_code == 200:
                        st.success(f"✅ Successfully registered {reg_name}!")
                        st.json(res.json().get('person', {}))
                    else:
                        st.error(f"❌ API Error: {res.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"📡 Connection Failed: {e}")

# --- TAB 2: VERIFICATION ---
with tab2:
    st.header("Identify Person")
    
    verify_source = st.radio("Search Source:", ["Camera", "Upload File"], 
                             horizontal=True, key="ver_src_toggle")
    
    verify_img = None
    if verify_source == "Camera":
        verify_img = st.camera_input("Capture face for matching", key="ver_cam_widget")
    else:
        verify_img = st.file_uploader("Upload face for matching", type=['jpg', 'jpeg', 'png'], key="ver_file_widget")

    if st.button("Search Database", type="primary", key="btn_search"):
        if verify_img is None:
            st.error("⚠️ Please provide an image to search.")
        else:
            img_bytes = verify_img.getvalue()
            files = {'image': ('verify.jpg', img_bytes, 'image/jpeg')}
            
            with st.spinner("Searching Vector Database in IRIS..."):
                try:
                    res = requests.post(f"{API_URL}/verify", files=files)
                    if res.status_code == 200:
                        result = res.json()
                        st.balloons()
                        st.success(f"🎯 Match Found! Confidence: {result['confidence']:.2%}")
                        st.write(result['person'])
                    elif res.status_code == 404:
                        st.warning("👤 Unknown person. No match found above threshold.")
                    else:
                        st.error(f"❌ Error: {res.text}")
                except Exception as e:
                    st.error(f"📡 Connection Failed: {e}")