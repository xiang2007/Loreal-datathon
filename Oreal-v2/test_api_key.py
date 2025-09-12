"""
Test script to verify API key loading
"""
import os
from dotenv import load_dotenv

print("🔍 Testing API Key Loading...")
print(f"Current working directory: {os.getcwd()}")

# Try loading .env file
env_loaded = load_dotenv()
print(f"✅ .env file loaded: {env_loaded}")

# Check if API key is in environment
api_key = os.getenv('GEMINI_API_KEY')
print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")

if api_key:
    print(f"🔑 API Key (first 10 chars): {api_key[:10]}...")
    print(f"🔑 API Key length: {len(api_key)}")
else:
    print("❌ GEMINI_API_KEY not found")
    print("💡 Make sure you have a .env file with GEMINI_API_KEY=your_key")

# List all environment variables that start with GEMINI
print("\n🔍 All GEMINI-related environment variables:")
for key, value in os.environ.items():
    if 'GEMINI' in key.upper():
        print(f"  {key}: {value[:10]}..." if value else f"  {key}: (empty)")

# Test Gemini import
try:
    import google.generativeai as genai
    print("\n✅ google-generativeai imported successfully")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini model configured successfully")
            
            # Test a simple generation
            response = model.generate_content("Say hello")
            print(f"✅ Test generation successful: {response.text[:50]}...")
            
        except Exception as e:
            print(f"❌ Gemini configuration failed: {e}")
    
except ImportError as e:
    print(f"❌ Failed to import google-generativeai: {e}")