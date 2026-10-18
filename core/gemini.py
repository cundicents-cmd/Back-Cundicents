from google import genai
from core.config_gemini import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)