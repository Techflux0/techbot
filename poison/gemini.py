import os
from dotenv import load_dotenv
import google.generativeai as genai
from storage.database import add_bad_word
load_dotenv()
genai.configure(api_key=os.getenv("BAD_WORDS"))
model = genai.GenerativeModel("models/gemini-2.5-pro-exp-03-25")
# print("api_key:", os.getenv("BAD_WORDS")) # Uncomment for debugging
def is_offensive_with_gemini(text: str) -> bool:
    try:
        prompt = f"""
Is there any offensive word in this message? If yes, return only the most offensive word used (even in disguised form), otherwise return "None".

Message: "{text}"
"""
        response = model.generate_content(prompt)
        result = response.text.strip().lower()

        if result and result != "none":
            add_bad_word(result)
           # print(f"Detected & added: {result}") # Uncomment for debugging
            return True
        return False
    except Exception as e:
        print("error:", e) # Uncomment for debugging
        return False
