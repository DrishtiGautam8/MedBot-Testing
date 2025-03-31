import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# # Configure Gemini API
# genai.configure(api_key=GEMINI_API_KEY)

# def list_gemini_models():
#     print("\n✅ Available Gemini Models:\n")
#     try:
#         models = genai.list_models()
#         for model in models:
#             # Filter out invalid arguments (e.g., max_temperature)
#             try:
#                 print(f"👉 {model.name}")
#             except TypeError as e:
#                 print(f"❌ Error loading model {model}: {e}")
#     except Exception as e:
#         print(f"❌ Failed to list Gemini models: {e}")

# if __name__ == "__main__":
#     list_gemini_models()





from groq import Groq

client = Groq(api_key="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")

# List available models
models = client.models.list()
print("\nAvailable Groq Models:\n")
for model in models.data:
    print(f"👉 {model.id}")
