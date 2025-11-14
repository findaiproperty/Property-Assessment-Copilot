import sys
import os

print("🔍 AI Configuration Debug")

# Check Python version and packages
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Test Google Generative AI import
try:
    import google.generativeai as genai
    print("✅ google.generativeai imported successfully")
    
    # List available attributes in genai
    print("📋 Available in genai module:")
    for attr in dir(genai):
        if not attr.startswith('_'):
            print(f"  - {attr}")
            
except ImportError as e:
    print(f"❌ Failed to import google.generativeai: {e}")
    
    # Check what's installed
    try:
        import pkg_resources
        installed_packages = [pkg.key for pkg in pkg_resources.working_set]
        if 'google-generativeai' in installed_packages:
            print("📦 google-generativeai is installed but can't be imported")
        else:
            print("📦 google-generativeai is NOT installed")
    except:
        print("📦 Could not check installed packages")

# Test API key configuration
API_KEY = "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
print(f"\n🔑 Testing API Key: {API_KEY[:10]}...")

if 'genai' in sys.modules:
    try:
        genai.configure(api_key=API_KEY)
        print("✅ API key configured")
        
        # Test listing models
        try:
            models = genai.list_models()
            print(f"✅ Available models: {len(list(models))}")
            
            # Test a simple generation
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content("Say 'TEST' in one word.")
            print(f"✅ API test successful: {response.text}")
            
        except Exception as e:
            print(f"❌ Model test failed: {e}")
            
    except Exception as e:
        print(f"❌ API configuration failed: {e}")
