"""列出可用的 Gemini 模型"""
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=api_key)

print("可用的 Gemini 模型：\n")
for model in client.models.list():
    print(f"- {model.name}")
    if hasattr(model, 'supported_generation_methods'):
        print(f"  支持的方法: {model.supported_generation_methods}")
