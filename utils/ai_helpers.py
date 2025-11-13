import os
import json
import re

# Import Google Gemini with error handling  
try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError as e:
    GOOGLE_AVAILABLE = False
    print(f"❌ Google Generative AI import failed: {e}")

class PropertyAIAnalyzer:
    def __init__(self):
        self.gemini_available = False
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize Google Gemini API"""
        print("🔧 Setting up Gemini API...")
        
        # Get API key from Streamlit secrets
        try:
            import streamlit as st
            self.google_key = st.secrets.get("GOOGLE_API_KEY", "")
            print(f"🔑 Key from secrets: {'Found' if self.google_key else 'NOT FOUND'}")
            if self.google_key:
                print(f"🔑 Key length: {len(self.google_key)}")
                print(f"🔑 Key starts with: {self.google_key[:10]}...")
        except Exception as e:
            print(f"❌ Failed to read secrets: {e}")
            self.google_key = os.getenv('GOOGLE_API_KEY', '')
            print(f"🔑 Key from env: {'Found' if self.google_key else 'NOT FOUND'}")
        
        # Google Gemini setup
        if not GOOGLE_AVAILABLE:
            print("❌ google-generativeai package not available")
            self.gemini_available = False
            return
            
        if not self.google_key:
            print("❌ No Google API key found")
            self.gemini_available = False
            return
        
        try:
            print("🔄 Configuring Gemini...")
            genai.configure(api_key=self.google_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            # Test the configuration with a simple call
            print("🧪 Testing API connection...")
            response = self.gemini_model.generate_content("Say 'API connected' in one word.")
            print(f"✅ API test response: {response.text}")
            
            self.gemini_available = True
            print("🎉 Google Gemini configured successfully!")
            
        except Exception as e:
            print(f"❌ Google Gemini setup failed: {e}")
            self.gemini_available = False
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini"""
        if not self.gemini_available:
            error_msg = "❌ Google Gemini not configured. "
            if not GOOGLE_AVAILABLE:
                error_msg += "Package not installed."
            elif not hasattr(self, 'google_key') or not self.google_key:
                error_msg += "API key not found in secrets."
            else:
                error_msg += "Configuration failed."
            return error_msg
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            print("🤖 Sending request to Gemini...")
            response = self.gemini_model.generate_content(prompt)
            print("✅ Received response from Gemini")
            return response.text
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            if "quota" in error_msg.lower():
                return "❌ Google API quota exceeded. Free tier has daily limits. Try again tomorrow."
            elif "API key" in error_msg or "key" in error_msg.lower():
                return "❌ Invalid Google API key. Please check your key configuration in Streamlit secrets."
            elif "safety" in error_msg.lower():
                return "⚠️ Content safety filters triggered. Please try different property details."
            else:
                return f"Google Gemini error: {error_msg}\n\nPlease try again."
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt for Gemini"""
        return f"""
You are an expert real estate investment analyst. Analyze this property for investment potential.

PROPERTY DETAILS:
- Address: {property_data.get('address', 'Not specified')}
- Type: {property_data.get('property_type', 'Not specified')}
- Bedrooms: {property_data.get('bedrooms', 'N/A')}
- Bathrooms: {property_data.get('bathrooms', 'N/A')}
- Square Feet: {property_data.get('square_feet', 'N/A')}
- Year Built: {property_data.get('year_built', 'N/A')}
- Condition: {property_data.get('condition', 'N/A')}
- Purchase Price: ${property_data.get('purchase_price', 0):,}

COMPARABLE PROPERTIES ({len(comps_data.get('comparables', []))} properties):
{json.dumps(comps_data.get('comparables', []), indent=2)}

Please provide a comprehensive but concise analysis with these specific sections:

1. **Rental Value Estimate**: Provide a monthly rental range based on comparables
2. **Gross Rental Yield**: Calculate (Annual Rent / Purchase Price) as percentage
3. **Demand Assessment**: Rate as High/Medium/Low based on market data
4. **Improvement Suggestions**: 3-5 cost-effective upgrades to increase value
5. **Flip Potential**: Assess as Strong/Moderate/Poor with reasoning
6. **Investment Recommendation**: Overall verdict and key considerations

Be data-driven and reference the comparable properties in your analysis. Keep it practical for real estate investors.
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

def get_free_apis():
    """Instructions for getting free API keys"""
    return {
        "Google Gemini": "✅ API Key configured via Streamlit Secrets"
    }
