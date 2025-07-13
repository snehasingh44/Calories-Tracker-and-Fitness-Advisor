from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import logging
from datetime import datetime
import re
from fpdf import FPDF
import tempfile

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Function to get response from the Gemini API
def get_gemini_response(image, prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([image[0], prompt])
        logger.info('Gemini API response received')
        return response.text
    except Exception as e:
        logger.error(f'Error generating response: {str(e)}')
        return f"Error generating response: {str(e)}"

# Function to process image and prepare for the API
def input_image_setup(uploaded_file):
    try:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": "image/jpeg", "data": bytes_data}]
        logger.info('Image processed successfully')
        return image_parts
    except Exception as e:
        logger.error(f'Error processing image: {str(e)}')
        raise ValueError(f"Error processing image: {str(e)}")

# Function to generate PDF from text
def generate_pdf(text, filename="meal_analysis.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    lines = text.split('\n')
    for line in lines:
        pdf.multi_cell(0, 10, line)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    return tmp_file.name

# Function for exercise recommendations
def get_exercise_recommendations(goal, age, weight, calories_today):
    try:
        prompt = f"""
        You are a fitness expert. Based on the user's goal: {goal}, age: {age} years, weight: {weight} kg, and calories consumed today: {calories_today} kcal,
        provide a personalized daily exercise and yoga routine. Include types of exercises, durations, and intensity levels suitable for this profile.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([prompt])
        logger.info('Exercise recommendations generated')
        return response.text
    except Exception as e:
        logger.error(f'Error generating exercise recommendations: {str(e)}')
        return f"Error generating exercise recommendations: {str(e)}"

# Streamlit app configuration
st.set_page_config(page_title="Calorie Tracker & Fitness Advisor", page_icon="🍎", layout="centered")

# Custom CSS styling
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        color: #eee;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 1rem 3rem;
    }
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        color: #bb86fc;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 5px #bb86fc;
    }
    .response-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #cf94ff;
        background-color: #1f1f1f;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 0 10px #bb86fc55;
        white-space: pre-wrap;
    }
    img {
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(187,134,252,0.6);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown('<div class="main-header">Calorie Tracker & Fitness Advisor</div>', unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.header("🍽 Meal Preferences & Daily Limits")
meal_type = st.sidebar.selectbox("Meal Type", ["Select Meal Type", "Breakfast", "Lunch", "Dinner", "Snack"])
daily_limit = st.sidebar.number_input("Daily Calorie Limit (kcal)", min_value=500, max_value=5000, step=50)

st.sidebar.header("💪 Fitness Profile")
exercise_goal = st.sidebar.selectbox("Fitness Goal", ["Select Your Goal", "Weight Loss", "Muscle Gain", "Maintain Fitness", "Improve Flexibility"])
age = st.sidebar.number_input("Age", min_value=10, max_value=100)
weight = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200)

# Initialize session state
if "selected_image" not in st.session_state:
    st.session_state.selected_image = None
if "meal_history" not in st.session_state:
    st.session_state.meal_history = []
if "total_calories" not in st.session_state:
    st.session_state.total_calories = 0

# Tabs for input and analysis
tab1, tab2, tab3 = st.tabs(["📷 Capture Image", "📁 Upload Image", "🏋️ Exercise Recommendations"])

with tab1:
    st.markdown("#### Use your camera to take a picture of your meal")
    camera_image = st.camera_input("Capture your food")
    if camera_image:
        st.session_state.selected_image = camera_image

with tab2:
    st.markdown("#### Upload an image of your meal")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.session_state.selected_image = uploaded_file

# Validate required inputs
valid_inputs = all([
    meal_type != "Select Meal Type",
    exercise_goal != "Select Your Goal",
    daily_limit,
    age,
    weight
])

# Image analysis
if st.session_state.selected_image and valid_inputs:
    try:
        image = Image.open(st.session_state.selected_image)
        st.image(image, caption="Selected Meal Image", use_column_width=True)
        image_data = input_image_setup(st.session_state.selected_image)

        input_prompt = """
        You are a professional nutritionist. Analyze the food in the image and:
        1) List each food item with estimated calorie content.
        2) Calculate total calories for the meal.
        3) Assess whether the meal is healthy.
        4) If unhealthy, provide suggestions to improve it.
        Format:
        1. Item 1 - XX calories
        2. Item 2 - XX calories
        ----
        Total Calories: XXX kcal
        Healthy or Unhealthy
        Suggestions:
        - ...
        """

        with st.spinner("Analyzing meal with AI..."):
            response_text = get_gemini_response(image_data, input_prompt)

        logger.info(f"Gemini response:\n{response_text}")

        # More flexible regex to capture total calories
        calories_match = re.search(r"total\s*calories\D+?(\d+)", response_text.lower())
        calories_this_meal = int(calories_match.group(1)) if calories_match else 0
        st.session_state.total_calories += calories_this_meal

        st.session_state.meal_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "meal_type": meal_type,
            "calories": calories_this_meal,
            "analysis": response_text
        })

        st.markdown("### 🥗 Nutritional Analysis")
        st.markdown(f'<div class="response-text">{response_text}</div>', unsafe_allow_html=True)

        st.markdown(f"### 🔥 Total Calories Today: {st.session_state.total_calories} / {daily_limit} kcal")
        st.progress(min(st.session_state.total_calories / daily_limit, 1.0))

        if "unhealthy" in response_text.lower():
            st.warning("⚠️ This meal may be unhealthy. Consider the suggestions above.")
        elif "healthy" in response_text.lower():
            st.success("✅ This meal looks healthy! Keep it up!")

        pdf_path = generate_pdf(response_text)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download This Meal Report (PDF)",
                data=f,
                file_name=f"meal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error processing image or generating analysis: {e}")
elif st.session_state.selected_image and not valid_inputs:
    st.warning("⚠️ Please fill out all sidebar inputs before proceeding.")

# Exercise tab
with tab3:
    st.markdown("### 🏋️ Personalized Exercise & Yoga Routine")
    if st.button("Generate Exercise Recommendations"):
        if not valid_inputs:
            st.warning("⚠️ Please complete all sidebar inputs.")
        else:
            with st.spinner("Generating your customized exercise routine..."):
                exercise_text = get_exercise_recommendations(exercise_goal, age, weight, st.session_state.total_calories)
                st.markdown(f'<div class="response-text">{exercise_text}</div>', unsafe_allow_html=True)

# Meal history section
st.markdown("---")
st.markdown("## 📚 Meal History")
if st.session_state.meal_history:
    for i, meal in enumerate(reversed(st.session_state.meal_history[-10:]), 1):
        st.markdown(f"**{i}. [{meal['timestamp']}] {meal['meal_type']} - {meal['calories']} kcal**")
        with st.expander("View analysis details"):
            st.text(meal['analysis'])
else:
    st.info("No meals logged yet. Upload or capture a meal image to start!")

# Footer
st.markdown("""
<div style="text-align:center; color:#888; margin-top:3rem; font-size:0.9rem;">
    Made with ❤️ using Streamlit & Google Gemini API | Your Personal Calorie Tracker & Fitness Advisor
</div>
""", unsafe_allow_html=True)
