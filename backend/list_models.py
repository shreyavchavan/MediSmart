import google.generativeai as genai
import os

# Hardcoded key from main.py for debugging
GEMINI_API_KEY = "AIzaSyA81BhVCBvHv_naFg1aflaPIcVw0k4cyXg"
genai.configure(api_key=GEMINI_API_KEY)

print("Listing available models...")
try:
    with open("available_models.txt", "w") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                f.write(m.name + "\n")
    print("Models written to available_models.txt")
except Exception as e:
    print(f"Error listing models: {e}")
