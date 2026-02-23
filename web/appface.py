import streamlit as st
import requests

API_URL = "http://facial-matching-api:5000/api"

st.set_page_config(page_title="IRIS Face Recognition", layout="wide")

try:
    response = requests.get(f"{API_URL}/status", timeout=1)
    if response.status_code == 200:
        status_data = response.json()
        if status_data.get("status") == "loading":
            st.warning("⏳ The AI ​​models are being loaded onto the server. The first run may take a few minutes.")
        elif status_data.get("status") == "error":
            st.error("❌ An error occurred while loading the AI ​​models on the server..")
except:
    pass 

tab1, tab2, tab3, tab4 = st.tabs(["👤 Register User", "🔍 Search / Verify", "📄 Registered List", "👪 Family Resemblance"])

with tab1:
    
    if "reset_key" not in st.session_state:
        st.session_state["reset_key"] = 0

    def clear_form():
        st.session_state["input_name"] = ""
        st.session_state["input_ssn"] = ""
        st.session_state["reset_key"] += 1

    col1, col2, col3 = st.columns(3)
    with col1:
        reg_source = st.radio("Select Image Source:", ["Camera", "Upload File"], 
                          horizontal=True, key="reg_src_toggle")
    with col2:
        reg_name = st.text_input("Full Name", key="input_name")
    with col3:
        reg_ssn = st.text_input("SSN / ID Number", key="input_ssn")
    
    reg_img = None
    if reg_source == "Camera":
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            reg_img = st.camera_input("Take a registration photo", key=f"reg_cam_widget_{st.session_state.reset_key}", label_visibility="collapsed")
    else:
        reg_img = st.file_uploader("Choose a registration photo", type=['jpg', 'jpeg', 'png'], key=f"reg_file_widget_{st.session_state.reset_key}")

    bcol1, bcol2 = st.columns([1, 5])
    with bcol1:
        submit = st.button("Finalize Registration", type="primary", key="btn_reg")
    with bcol2:
        st.button("Reset Form", on_click=clear_form, key="btn_reset")

    if submit:
        if not reg_name or not reg_ssn:
            st.warning("⚠️ Please provide Name and SSN.")
        elif reg_img is None:
            st.error("⚠️ No image detected. Please capture a photo or upload a file first.")
        else:
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

with tab2:
    st.header("Identify Person")
    
    verify_source = st.radio("Search Source:", ["Camera", "Upload File"], 
                             horizontal=True, key="ver_src_toggle")
    
    verify_img = None
    if verify_source == "Camera":
        # Use columns to constrain the camera input width and center it
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            verify_img = st.camera_input("Capture face for matching", key="ver_cam_widget", label_visibility="collapsed")
    else:
        verify_img = st.file_uploader("Upload a face for matching", type=['jpg', 'jpeg', 'png'], key="ver_file_widget")

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

with tab3:
    st.header("Registered People")
    
    if st.button("🔄 Refresh List"):
        pass 
        
    try:
        res = requests.get(f"{API_URL}/people")
        if res.status_code == 200:
            people = res.json().get("people", [])
            if people:
                st.dataframe(people, use_container_width=True)
            else:
                st.info("No registered people found.")
        else:
            st.error("Error fetching data from API.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

with tab4:
    st.header("Calculate Family Resemblance")
    st.info("Upload photos of the father, child, and mother to see the facial similarity percentages.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Father")
        father_name = st.text_input("Father's Name", key="father_name")
        father_img = st.file_uploader("Upload Father's Photo", type=['jpg', 'jpeg', 'png'], key="father_img")
        if father_img:
            st.image(father_img)

    with col2:
        st.subheader("Child")
        child_name = st.text_input("Child's Name", key="child_name")
        child_img = st.file_uploader("Upload Child's Photo", type=['jpg', 'jpeg', 'png'], key="child_img")
        if child_img:
            st.image(child_img)

    with col3:
        st.subheader("Mother")
        mother_name = st.text_input("Mother's Name", key="mother_name")
        mother_img = st.file_uploader("Upload Mother's Photo", type=['jpg', 'jpeg', 'png'], key="mother_img")
        if mother_img:
            st.image(mother_img)
    
    st.write("---")

    if st.button("Calculate Resemblance", type="primary", key="btn_family"):
        if not father_img or not child_img or not mother_img:
            st.warning("⚠️ Please upload all three photos.")
        else:
            files = {
                'father_image': ('father.jpg', father_img.getvalue(), 'image/jpeg'),
                'child_image': ('child.jpg', child_img.getvalue(), 'image/jpeg'),
                'mother_image': ('mother.jpg', mother_img.getvalue(), 'image/jpeg')
            }
            
            with st.spinner("Analyzing faces and calculating resemblance..."):
                try:
                    res = requests.post(f"{API_URL}/verify_family", files=files)
                    if res.status_code == 200:
                        result = res.json()
                        father_resemblance = result.get("resemblance_to_father", 0)
                        mother_resemblance = result.get("resemblance_to_mother", 0)

                        st.success("✅ Analysis Complete!")
                        
                        res_col1, res_col2 = st.columns(2)
                        res_col1.metric(label=f"Resemblance to {father_name or 'Father'}", value=f"{father_resemblance:.2f}%")
                        res_col2.metric(label=f"Resemblance to {mother_name or 'Mother'}", value=f"{mother_resemblance:.2f}%")

                    else:
                        st.error(f"❌ API Error: {res.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"📡 Connection Failed: {e}")