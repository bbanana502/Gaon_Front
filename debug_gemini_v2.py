import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyA29PHUX7dlyev9Q5OXCWlracAMfJ23ksc"

print(f"Configuring with Key: {GEMINI_API_KEY[:5]}...")
genai.configure(api_key=GEMINI_API_KEY)

# Try 2.0 Flash
print("\n--- Testing gemini-2.0-flash ---")
try:
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Hello, this is a test.")
    print("SUCCESS: ", response.text)
except Exception as e:
    print("FAILURE: ", e)

# Try Pro just in case
print("\n--- Testing gemini-pro ---")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, this is a test.")
    print("SUCCESS: ", response.text)
except Exception as e:
    print("FAILURE: ", e)
