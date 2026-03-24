import os
import google.generativeai as genai
from dotenv import load_dotenv

# Force load the hidden .env variables before authentication so the API key doesn't return None
load_dotenv()

# Securely configure the API key imported from the backend environment
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize the lightning fast Gemini 2.5 Flash model specifically designed for massive context handling
model = genai.GenerativeModel("gemini-2.5-flash")

def generate_summary(text):
    # Safeguard: Images often contain very little text. 
    # If the text is incredibly short, it takes less time to read than summarization API latency.
    if len(text.split()) < 40:
        return text

    # Since Gemini 1.5 Flash has a massive 1M token context window, 
    # we completely bypass the old Map-Reduce chunking logic.
    # However, to prevent massively dense 10MB+ files from exceeding Google's maximum REST JSON payload limit,
    # we logically cap the extraction buffer to the first 500,000 characters (~125,000 tokens).
    safe_text = text[:500000]

    prompt = f"Please aggressively read the following document and write a very clear, concise, highly intelligent summary covering all the main structural points in roughly 150 words.\n\nDOCUMENT CONTENT:\n{safe_text}"
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "A cloud error occurred while communicating with the Gemini AI. Please check your network or API limits and try again."