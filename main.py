import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import random
from datetime import datetime, timedelta


# Load environment variables

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", None)

if GOOGLE_API_KEY is None:
    import os
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Load vehicle Excel database
vehicle_df = pd.read_excel("rto_data.xlsx")
vehicle_df.columns = vehicle_df.columns.str.strip()

# Streamlit UI
st.set_page_config(page_title="RTO Challan Simulator", page_icon="🚦")
st.title("🚦 RTO Challan Simulator using Gemini AI")

# Upload section
uploaded_file = st.file_uploader("📷 Upload Vehicle Image", type=["png", "jpg", "jpeg"])

# Violation type selector
violation_type = st.selectbox("⚠️ Select Observed Violation", [
    "Overspeeding", "Signal Jumping", "No Seatbelt", "Wrong Lane",
    "Driving without License", "Expired Insurance", "Expired PUC"
])

if uploaded_file and violation_type:
    try:
        image = Image.open(uploaded_file)
        resized_image = image.resize((400, 250))
        st.image(resized_image, caption="📸 Uploaded Vehicle Image", use_container_width=False)
    except Exception as e:
        st.error(f"❌ Failed to load image: {e}")
        st.stop()

    if st.button("🔎 Search for Violations"):
        # Plate detection
        with st.spinner("🔍 Detecting Number Plate..."):
            prompt = "Extract the license plate number from this Indian vehicle image. Just return the number like KA01AB1234."
            try:
                result = model.generate_content([prompt, image])
                plate_number = result.text.strip().replace(" ", "").upper()
            except Exception as e:
                st.error(f"❌ Failed to detect plate number: {e}")
                st.stop()

        st.success(f"✅ Detected Vehicle Number: `{plate_number}`")

        # BH-series check
        if "BH" in plate_number:
            st.info("🟢 This is a **BH-series** registration.")

        # Match in Excel DB
        vehicle_df["Vehicle No"] = vehicle_df["Vehicle No"].str.strip().str.replace(" ", "").str.upper()
        match = vehicle_df[vehicle_df['Vehicle No'] == plate_number]

        if not match.empty:
            owner = match.iloc[0]["Name"]
            vehicle = match.iloc[0]["Vehicle No"]
            address = match.iloc[0].get("Address", "Unknown")

            st.markdown("### 📋 Vehicle Information")
            col1, col2 = st.columns(2)
            col1.markdown(f"**👤 Owner:** {owner}")
            col1.markdown(f"**🚘 Reg. Number:** {vehicle}")
            col2.markdown(f"**📍 Address:** {address}")
            col2.markdown(f"**🔒 Violation:** {violation_type}")

            # Reasoning
            with st.spinner("🧠 Determining Violation Details..."):
                violation_prompt = f"Vehicle number {plate_number} was observed {violation_type.lower()} in a 60 km/h speed zone. Determine the violated rule under Indian traffic law and applicable fine."
                violation_info = model.generate_content(violation_prompt).text.strip()

            st.markdown("### ⚖️ Violation Reasoning")
            st.info(violation_info)

            # Metadata
            challan_number = f"CH{random.randint(100000, 999999)}"
            violation_datetime = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            date_only, time_only = violation_datetime.split()

            # 💰 Assign fine based on violation type
            fine_mapping = {
                "Overspeeding": 1000,
                "Signal Jumping": 500,
                "No Seatbelt": 200,
                "Wrong Lane": 400,
                "Driving without License": 5000,
                "Expired Insurance": 2000,
                "Expired PUC": 1000
            }

            fine_amount = fine_mapping.get(violation_type, 500)  # Default fine if not found

            # Officer generation
            with st.spinner("👮 Assigning Officer..."):
                officer_prompt = "Generate a realistic Indian RTO officer's name and designation like 'Rakesh Sharma, Motor Vehicle Inspector'"
                officer_result = model.generate_content(officer_prompt).text.strip()

            summary_prompt = f"""
                    Generate a concise RTO challan using these fields:

                    - Challan Number: {challan_number}
                    - Date of Violation: {date_only}
                    - Time of Violation: {time_only}
                    - Vehicle Number: {plate_number}
                    - Owner Name: {owner}
                    - Vehicle Type: [Suggest appropriate type like Car, Bike, Auto based on {plate_number}]
                    - Owner Address: {address}
                    - Violation Type: {violation_type}
                    - Fine Amount: ₹{fine_amount} (reasonable based on Indian traffic rules)
                    - Due Date: {(datetime.now() + timedelta(days=15)).strftime("%d-%m-%Y")}
                    - Officer Name: {officer_result.split(',')[0]}
                    - Designation: {officer_result.split(',')[1] if ',' in officer_result else 'Motor Vehicle Inspector'}

                    Make it short and formal. No legal reasoning or long explanation needed.
                    """

            st.subheader("🧾 Final Challan Summary")
            challan_text = model.generate_content(summary_prompt).text.strip()

            st.text_area("Challan Preview", challan_text, height=400)

            # Download button
            st.download_button(
                label="📄 Download Challan as .txt",
                data=challan_text,
                file_name=f"challan_{challan_number}.txt",
                mime="text/plain"
            )

        else:
            st.error("❌ Vehicle not found in the database.")
