import sys
import os

def test_environment():
    print("🔍 Testing Environment Setup")
    print(f"Python: {sys.version}")
    print(f"Directory: {os.getcwd()}")
    
    # Test imports
    try:
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai: Imported")
        
        # Test API
        API_KEYS = [
            "AIzaSyDA1gKnB7WwNiOwa7mzw0Wn7vJHK1t6YVg",
            "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
        ]
        
        for i, key in enumerate(API_KEYS):
            try:
                genai.configure(api_key=key)
                models = list(genai.list_models())
                print(f"✅ API Key {i+1}: Working ({len(models)} models available)")
                
                # Test generation
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content("Say 'TEST OK'")
                print(f"✅ Generation test: '{response.text}'")
                break
                
            except Exception as e:
                print(f"❌ API Key {i+1}: Failed - {str(e)[:100]}")
                
    except ImportError as e:
        print(f"❌ google.generativeai: {e}")

if __name__ == "__main__":
    test_environment()
