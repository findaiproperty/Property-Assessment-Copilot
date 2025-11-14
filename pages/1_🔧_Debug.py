import streamlit as st
import sys
import os
import traceback

st.title("🔧 AI Debugger")

st.header("1. Python Environment")
st.write(f"Python version: {sys.version}")
st.write(f"Current directory: {os.getcwd()}")
st.write(f"Files in directory: {os.listdir('.')}")

st.header("2. Package Check")
try:
    import google.generativeai as genai
    st.success("✅ google.generativeai imported")
    
    # Show version
    try:
        import pkg_resources
        version = pkg_resources.get_distribution("google-generativeai").version
        st.write(f"Version: {version}")
    except:
        st.write("Version: Unknown")
        
except ImportError as e:
    st.error(f"❌ Import failed: {e}")

st.header("3. API Key Test")
API_KEY = "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"

if st.button("Test API Key"):
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        st.success("✅ API key configured")
        
        # Test with a simple request
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("What is 2+2? Answer with one number only.")
        st.success(f"✅ API working! Response: {response.text}")
        
    except Exception as e:
        st.error(f"❌ API test failed: {e}")
        st.code(traceback.format_exc())

st.header("4. Check Current AI Analyzer")
if 'ai_analyzer' in st.session_state:
    analyzer = st.session_state.ai_analyzer
    st.write(f"Gemini Available: {analyzer.gemini_available}")
else:
    st.warning("AI Analyzer not in session state")
