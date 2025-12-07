import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyA29PHUX7dlyev9Q5OXCWlracAMfJ23ksc"
genai.configure(api_key=GEMINI_API_KEY)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
