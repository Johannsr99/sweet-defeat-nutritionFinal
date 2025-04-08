import streamlit as st
from PIL import Image
import requests
import base64
import json
import io

# --- GOOGLE VISION API SETUP ---
GOOGLE_VISION_API_KEY = "AIzaSyCArxETVDKlD-97qLydGweFxut959syrUk"
VISION_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_VISION_API_KEY}"

# --- STREAMLIT UI ---
st.set_page_config(page_title="Sweet Defeat – Nutrition Check", page_icon="🍽️", layout="centered")
st.title("🍽️ Sweet Defeat – Nutrition Check")
st.subheader("Upload a photo of your meal and get nutritional information.")

uploaded_file = st.file_uploader("📸 Upload your meal photo", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your uploaded photo", use_column_width=True)

    # --- Convert image to Base64 ---
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    # --- Send request to Google Vision API ---
    vision_payload = {
        "requests": [
            {
                "image": {"content": img_base64},
                "features": [{"type": "LABEL_DETECTION", "maxResults": 3}]
            }
        ]
    }

    st.info("🔍 Analyzing image...")

    response = requests.post(VISION_URL, json=vision_payload)
    labels = response.json().get("responses", [])[0].get("labelAnnotations", [])

    if labels:
        top_label = labels[0]["description"]
        st.success(f"🍽️ Detected food item: **{top_label}**")

        # --- Search Open Food Facts API ---
        query = top_label.replace(" ", "%20").lower()
        off_response = requests.get(f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=1")

        if off_response.status_code == 200 and off_response.json().get("products"):
            product = off_response.json()["products"][0]
            nutriments = product.get("nutriments", {})

            kcal = nutriments.get("energy-kcal_100g", "N/A")
            carbs = nutriments.get("carbohydrates_100g", "N/A")
            fat = nutriments.get("fat_100g", "N/A")
            protein = nutriments.get("proteins_100g", "N/A")
            fiber = nutriments.get("fiber_100g", "N/A")

            st.markdown("**Estimated nutrition per 100g:**")
            st.markdown(f"""
            - 🔥 Calories: {kcal} kcal  
            - 🍞 Carbohydrates: {carbs} g  
            - 🥩 Protein: {protein} g  
            - 🧈 Fat: {fat} g  
            - 🌾 Fiber: {fiber} g
            """)
        else:
            st.warning("⚠️ No nutrition data found.")
    else:
        st.error("😕 No recognizable food item detected.")
else:
    st.info("Please upload a photo to begin.")
