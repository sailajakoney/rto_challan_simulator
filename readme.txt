🚦 RTO CHALLAN SIMULATOR using GEMINI AI
=========================================

This application allows users to upload a vehicle image, detect the number plate 
using Gemini AI (Vision), and simulate an RTO traffic challan with violation reasoning, 
owner details, fine, and challan generation.

🧠 Powered by: Google Gemini (Vision API)
🖥️ Interface: Streamlit
📄 Data Source: rto_data.xlsx (Vehicle database)

-----------------------------------------------------
🔧 INSTALLATION REQUIREMENTS
-----------------------------------------------------

1. Python Version
   - Python 3.8 or higher

2. Install Required Python Libraries
  -> Run this command in your terminal or command prompt:
   pip install streamlit pandas python-dotenv google-generativeai pillow openpyxl

3.  Gemini API Key
->Sign up at https://aistudio.google.com/app/apikey
Copy your API key.

4. Create a .env file in the root directory of your project with the following content:
->GOOGLE_API_KEY=your_gemini_api_key_here

5. Add your Excel file
->Make sure rto_data.xlsx is present in the same folder.

6. How to Run 
> streamlit run main.py

7.NOTES
->If a blurred image is uploaded, the AI may return incorrect or generic results like "KA01AB1234".

8.requiremnts.txt
 -> This file contains all the required libraries to be installed.
