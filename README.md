# Calories-Tracker-and-Fitness-Advisor
An AI-powered app that analyzes meal images using Google Gemini, tracks daily calorie intake, and provides personalized fitness and yoga plans. Built with Streamlit, it offers nutritional analysis, PDF reports, meal history, and goal-based exercise suggestions for a healthy lifestyle.
Key Features
1 Meal Image Analysis
2 Upload or capture an image of your meal. The app uses Google Gemini AI to:
3 Identify food items
4 Estimate calories per item
5 Calculate total meal calories
6 Assess healthiness
7 Provide improvement suggestions

Daily Calorie Tracker
Keep track of your total calorie intake throughout the day. Visual progress indicators help you stay within your daily calorie limit.

Fitness & Yoga Recommendations
Get personalized routines based on your:
1 Age
2 Weight
3 Fitness goal (Weight Loss, Muscle Gain, Maintain Fitness, etc.)

- Calories consumed
- PDF Report Generator
- Download a well-formatted PDF report of your meal analysis with one click.
- Meal History Log
- View your recent meal entries along with calorie info and full analysis.

🛠 Tech Stack
Frontend: Streamlit with custom CSS

Backend AI: Google Gemini API

PDF: FPDF

Image Handling: Pillow

Environment Management: dotenv

🚀 How to Run
Clone the repo:

bash

git clone https://github.com/snehasingh44/calorie-tracker.git
cd calorie-tracker
Install dependencies:

bash

pip install -r requirements.txt
Add your .env file with:

ini

GOOGLE_API_KEY=your_key
Run the app:

bash

streamlit run app.py
