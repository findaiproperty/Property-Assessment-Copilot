import sys
import os

# Test imports
try:
    import google.generativeai as genai
    print("✅ google-generativeai imported successfully")
except ImportError as e:
    print(f"❌ Failed to import google-generativeai: {e}")
    sys.exit(1)

# Test API key
API_KEY = "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
try:
    genai.configure(api_key=API_KEY)
    print("✅ API key configured")
    
    # Test model listing
    models = genai.list_models()
    print(f"✅ Available models: {len(models)} models found")
    
    # Test simple generation
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say 'TEST SUCCESSFUL' in one word.")
    print(f"✅ API test response: {response.text}")
    
except Exception as e:
    print(f"❌ API test failed: {e}")
