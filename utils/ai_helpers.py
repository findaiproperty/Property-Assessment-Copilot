import os
import json
import re
import sys

# Check if google-generativeai is installed
try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
    print("✅ google-generativeai package successfully imported")
except ImportError as e:
    GOOGLE_AVAILABLE = False
    print(f"❌ google-generativeai import failed: {e}")
    print("📦 Available packages:")
    for package in sorted(sys.modules.keys()):
        if 'google' in package or 'genai' in package:
            print(f"   - {package}")

class PropertyAIAnalyzer:
    def __init__(self):
        self.gemini_available = False
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize Google Gemini API with hardcoded key"""
        print("🔧 Setting up Gemini API...")
        print(f"📦 Google Generative AI available: {GOOGLE_AVAILABLE}")
        
        # HARDCODED API KEY
        self.google_key = "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
        print(f"🔑 API key configured: {bool(self.google_key)}")
        print(f"🔑 Key preview: {self.google_key[:10]}...")
        
        if not GOOGLE_AVAILABLE:
            print("❌ Cannot setup Gemini - package not available")
            self.gemini_available = False
            return
            
        if not self.google_key:
            print("❌ Cannot setup Gemini - no API key")
            self.gemini_available = False
            return
        
        try:
            print("🔄 Configuring Gemini API...")
            genai.configure(api_key=self.google_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini model created")
            
            # Test the configuration
            print("🧪 Testing API connection...")
            response = self.gemini_model.generate_content("Say 'Connected'")
            print(f"✅ API test successful: {response.text}")
            
            self.gemini_available = True
            print("🎉 Google Gemini fully configured and ready!")
            
        except Exception as e:
            print(f"❌ Gemini setup failed: {str(e)}")
            self.gemini_available = False
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini"""
        if not self.gemini_available:
            return "❌ Google Gemini is not available. Please check the server logs for configuration issues."
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            print("🤖 Sending analysis request to Gemini...")
            response = self.gemini_model.generate_content(prompt)
            print("✅ Analysis received successfully")
            return response.text
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            if "quota" in error_msg.lower():
                return "❌ API quota exceeded. Please try again later."
            elif "API key" in error_msg or "key" in error_msg.lower():
                return f"❌ API key issue: {error_msg}"
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Please modify your property details."
            else:
                return f"❌ Gemini API error: {error_msg}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt for Gemini"""
        return f"""
As a real estate investment expert, analyze this property:

PROPERTY:
- {property_data.get('bedrooms', 0)} bed, {property_data.get('bathrooms', 0)} bath
- {property_data.get('square_feet', 0)} sqft, {property_data.get('condition', 'Unknown')} condition
- Built in {property_data.get('year_built', 'Unknown')}
- Purchase price: ${property_data.get('purchase_price', 0):,}

COMPARABLE PROPERTIES:
{json.dumps(comps_data.get('comparables', []), indent=2)}

Provide analysis covering:
1. Estimated monthly rental value range
2. Gross rental yield percentage 
3. Market demand level (High/Medium/Low)
4. Top 3 value-add improvements
5. Flip potential assessment
6. Investment recommendation

Be concise and data-driven.
"""
    
    def extract_metrics(self, analysis_text):
        """Extract key metrics from AI analysis"""
        metrics = {
            'rental_value': 'See analysis',
            'yield': 'See analysis', 
            'demand': 'See analysis',
            'flip_potential': 'See analysis'
        }
        
        # Extract rental value
        rental_match = re.search(r'\$(\d{1,4}(?:,\d{3})*(?:\s*-\s*\$\d{1,4}(?:,\d{3})*)?)\s*(?:per month|monthly|rent)', analysis_text)
        if rental_match:
            metrics['rental_value'] = f"${rental_match.group(1)}/mo"
        
        # Extract yield percentage
        yield_match = re.search(r'(\d+\.?\d*)%\s*(?:yield|return)', analysis_text, re.IGNORECASE)
        if yield_match:
            metrics['yield'] = f"{yield_match.group(1)}%"
        
        # Extract demand level
        for level in ['High', 'Medium', 'Low']:
            if level in analysis_text and 'demand' in analysis_text.lower():
                metrics['demand'] = level
                break
        
        # Extract flip potential
        for potential in ['Strong', 'Good', 'Moderate', 'Fair', 'Poor']:
            if potential in analysis_text and any(word in analysis_text.lower() for word in ['flip', 'potential', 'candidate']):
                metrics['flip_potential'] = potential
                break
        
        return metrics
