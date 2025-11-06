import streamlit as st
import requests
from PIL import Image
import io
import base64
from random import randrange
import plotly.graph_objects as go
import os
from pathlib import Path
# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(page_title="🥚 EggCounting Dashboard", layout="wide")

# -------------------------------
# Custom CSS for Styling
# -------------------------------
st.markdown("""
<style>
            
/* General background */
.stApp {
    background-color: #f2f2f2;  /* light gray theme */
}

/*  Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #d9d9d9 !important;  /* slightly darker gray */
    color: #333333;
    border-right: 1px solid #cccccc;
}

/* Sidebar header text */
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: #222222;
    font-weight: 600;
}
.title {
    text-align: center;
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffb703;
    margin-bottom: 0.2rem;
}
.subtitle {
    text-align: center;
    color: #6c757d;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}
.stImage img {
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    object-fit: contain;
    max-height: 420px;
}
.results-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1.5rem;
    text-align: center;
}
.results-table th {
    background-color: #f1f5f9;
    color: #374151;
    font-weight: 600;
    padding: 10px;
    border-bottom: 2px solid #e5e7eb;
}
.results-table td {
    padding: 12px;
    font-size: 1.1rem;
    border-bottom: 1px solid #e5e7eb;
}
.status-ok {
    background-color: #dcfce7;
    color: #15803d;
    font-weight: 600;
    border-radius: 8px;
}
.status-notok {
    background-color: #fee2e2;
    color: #b91c1c;
    font-weight: 600;
    border-radius: 8px;
}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    height: 3rem;
    background-color: #3b82f6;
    color: white;
    font-size: 1rem;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #2563eb;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------
st.markdown('<div class="title">🥚 EggCounting Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Detect eggs, empty slots, and verify tray quality instantly.</div>', unsafe_allow_html=True)


# -------------------------------
# Backend API Configuration
# -------------------------------
API_URL = "http://127.0.0.1:8000/predict/"  # FastAPI backend endpoint

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.subheader("Upload Egg Tray Image")
    
    # Option to choose between upload, sample images, or webcam
    image_source = st.radio(
        "Select Image Source:",
        ["Upload Your Own", "Use Sample Image", "Capture from Webcam"],
        index=0
    )
    
    uploaded_file = None
    sample_image_path = None
    webcam_image = None
    
    if image_source == "Upload Your Own":
        uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image Preview", use_container_width=False)
            st.write("")
            predict_btn = st.button("🔍 Predict", use_container_width=True)
        else:
            predict_btn = False
    
    elif image_source == "Capture from Webcam":
        st.write("📸 Click the button below to capture an image:")
        st.info("💡 Tip: For best results, ensure good lighting and hold camera steady")
        webcam_image = st.camera_input("Take a picture")
        
        if webcam_image:
            st.write("")
            predict_btn = st.button("🔍 Predict", use_container_width=True)
        else:
            predict_btn = False
    
    else:  # Use Sample Image
        # Get sample images from the folder
        sample_folder = Path(__file__).parent.parent / "sample_images_for_testing"
        
        if sample_folder.exists():
            sample_images = list(sample_folder.glob("*.jpg")) + list(sample_folder.glob("*.jpeg")) + list(sample_folder.glob("*.png"))
            
            if sample_images:
                # Create friendly names for display
                sample_names = [f"Sample {i+1}" for i in range(len(sample_images))]
                
                selected_sample = st.selectbox(
                    "Choose a sample image:",
                    options=range(len(sample_images)),
                    format_func=lambda x: sample_names[x]
                )
                
                sample_image_path = sample_images[selected_sample]
                
                # Display the selected sample image
                st.image(str(sample_image_path), caption=f"{sample_names[selected_sample]} Preview", use_container_width=False)
                st.write("")
                predict_btn = st.button("🔍 Predict", use_container_width=True)
            else:
                st.warning("No sample images found in the folder.")
                predict_btn = False
        else:
            st.warning("Sample images folder not found.")
            predict_btn = False

# -------------------------------
# Layout-1
# -------------------------------
col1, col2 = st.columns([1.5, 1])
predection_completed= False

# -------- Left Column: Upload + Metrics --------
with col1:


    if predict_btn and (uploaded_file or sample_image_path or webcam_image):
        with st.spinner("Processing image... please wait"):
            # Send image to FastAPI backend (no saving)
            if uploaded_file:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            elif webcam_image:
                files = {"file": ("webcam_capture.jpg", webcam_image, "image/jpeg")}
            else:
                # For sample images, open and send as file
                with open(sample_image_path, "rb") as f:
                    files = {"file": (sample_image_path.name, f, "image/jpeg")}
                    try:
                        response = requests.post(API_URL, files=files, timeout=60)
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ API request failed: {e}")
                        st.stop()
            
            # For uploaded files or webcam, send normally
            if uploaded_file or webcam_image:
                try:
                    response = requests.post(API_URL, files=files, timeout=60)
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ API request failed: {e}")
                    st.stop()
                    
    if predict_btn and (uploaded_file or sample_image_path or webcam_image) and response.status_code == 200:
        try:
            # Decode base64 image returned from backend
            result = response.json()
            annotated_image_base64 = result["annotated_image_base64"]
            image_data = base64.b64decode(annotated_image_base64)
            annotated_image = Image.open(io.BytesIO(image_data))

            st.markdown("### 🖼️ Processed Result")
            st.image(annotated_image, caption="Processed Result", use_container_width=True)

            

            

            st.session_state.result = result  # Save result for col2


        except Exception as e:
            st.error(f"❌ Failed to load processed image: {e}")

    else:
        st.markdown("### See results here")
        st.info("Upload an image to preview and process the result here.")

# -------- Right Column: Output Visualization --------
with col2:
    if predict_btn and (uploaded_file or sample_image_path or webcam_image) and response.status_code == 200:
        try:

            tray_ok = result["tray_status"].lower() == "ok"
            tray_class = "status-ok" if tray_ok else "status-notok"

            # Render metrics table
            st.markdown("### 📊 Detection Results")
            st.markdown(f"""
                <table class="results-table">
                    <tr>
                        <th>Egg Tray Id</th>
                        <th>Tray Status</th>
                        <th>Number of Eggs</th>
                        <th>Empty Slots</th>
                    </tr>
                    <tr>
                        <td>{randrange(10)}</td>
                        <td class="{tray_class}">{'OK ✅' if tray_ok else 'Not OK ❌'}</td>
                        <td>{result['num_eggs']}</td>
                        <td>{result['num_empty_slots']}</td>
                    </tr>
                </table>
            """, unsafe_allow_html=True)
            predection_completed= True
            st.session_state.result = result  # Save result for col2




        except Exception as e:
            st.error(f"❌ Failed to load processed image: {e}")

    else:
        st.markdown("### 📊 Detection Results")
        st.info("Upload an image to preview and process the result here.")
# -------------------------------
# Layout-1
# -------------------------------
col3, col4 = st.columns([1, 1])
# -------- Left Column: Upload + Metrics --------
with col3:
    if predection_completed:
        try:
            # After rendering the metrics table
            st.markdown("### 📈 Production Shift Overview")

            # Dummy data for visualization
            shift_data = {
                "Shift Date": "23-05-2025",
                "Shift Time": "Day Shift",
                "Operator Name": "Krish",
                "Total Trays Inspected": 2300,
                "Go Trays": 2000,
                "No-Go Trays": 300,
                "Total Eggs Detected": 10000,
                "Empty Slots Detected": 200
            }

            # Bar chart values
            categories = [
                "Total Trays Inspected",
                "Go Trays",
                "No-Go Trays",
             
            ]
            values = [
                shift_data["Total Trays Inspected"],
                shift_data["Go Trays"],
                shift_data["No-Go Trays"],
             
            ]

            # Create Plotly bar chart
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=categories,
                        y=values,
                        marker_color=["#3b82f6", "#22c55e", "#ef4444"],
                        text=values,
                        textposition="auto",
                    )
                ]
            )

            fig.update_layout(
                title=f"Production Metrics overview- {shift_data['Shift Date']} ({shift_data['Shift Time']})",
                xaxis_title="Metrics",
                yaxis_title="Count",
                template="simple_white",
                plot_bgcolor="#f5f5f5",
                paper_bgcolor="#f5f5f5",
                title_font=dict(size=20, color="#333", family="Segoe UI"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#e5e7eb"),
                margin=dict(t=60, b=40)
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

   
      
        except Exception as e:
            st.error(f"❌ Failed to load processed image: {e}")
# -------- Right Column: Output Visualization --------
with col4:
    if predection_completed:
        try:
                       
            st.markdown(" ")
            # Dummy data for visualization
            shift_data = {
                "Shift Date": "23-05-2025",
                "Shift Time": "Day Shift",
                "Operator Name": "Krish",
                "Total Trays Inspected": 2300,
                "Go Trays": 2000,
                "No-Go Trays": 300,
                "Total Eggs Detected": 10000,
                "Empty Slots Detected": 200
            }

            # Bar chart values
            categories = [
        
                "Total Eggs Detected",
                "Empty Slots Detected"
            ]
            values = [
              
                shift_data["Total Eggs Detected"],
                shift_data["Empty Slots Detected"]
            ]

            # Create Plotly bar chart
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=categories,
                        y=values,
                        marker_color=[ "#facc15", "#a855f7"],
                        text=values,
                        textposition="auto",
                    )
                ]
            )

            fig.update_layout(
                title=f"production Incharge : Krish",
                xaxis_title="Metrics",
                yaxis_title="Count",
                template="simple_white",
                plot_bgcolor="#f5f5f5",
                paper_bgcolor="#f5f5f5",
                title_font=dict(size=20, color="#333", family="Segoe UI"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#e5e7eb"),
                margin=dict(t=60, b=40)
            )

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)


        except Exception as e:
            st.error(f"❌ Failed to load processed image: {e}")


# Add a note
st.markdown(
    """
    <p style="text-align:center; color:#666; font-size:14px; margin-top:10px;">
        📊 Note: This charts displays generic production data for demonstration purposes only.you can link your database to generate these graphs in real time 
    </p>
    """,
    unsafe_allow_html=True
)
# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Developed by Muddu Krishna Galavalli | AI-Powered Visual Inspection © 2025")