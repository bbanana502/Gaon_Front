import google.generativeai as genai
import os

# The key provided by the user
GEMINI_API_KEY = "AIzaSyA29PHUX7dlyev9Q5OXCWlracAMfJ23ksc"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, are you working?")
    print("SUCCESS")
    print(response.text)
except Exception as e:
    print("FAILURE")
    print(e)
