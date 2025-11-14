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
        self.gemini_model = None
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize Google Gemini API with hardcoded key"""
        print("🔧 Setting up Gemini API...")
        print(f"📦 Google Generative AI available: {GOOGLE_AVAILABLE}")
        
        if not GOOGLE_AVAILABLE:
            print("❌ Cannot setup Gemini - package not available")
            self.gemini_available = False
            return
        
        # HARDCODED API KEY - Replace if needed
        self.google_key = "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
        
        if not self.google_key or self.google_key == "YOUR_API_KEY_HERE":
            print("❌ Cannot setup Gemini - no valid API key")
            self.gemini_available = False
            return
            
        print(f"🔑 API key configured: {bool(self.google_key)}")
        print(f"🔑 Key preview: {self.google_key[:10]}...")
        
        try:
            print("🔄 Configuring Gemini API...")
            genai.configure(api_key=self.google_key)
            print("✅ Gemini API configured")
            
            # List available models to test connection
            print("📋 Checking available models...")
            models = genai.list_models()
            model_names = [model.name for model in models]
            print(f"Available models: {model_names}")
            
            # Use gemini-pro model
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini model created")
            
            # Test the configuration with a simple prompt
            print("🧪 Testing API connection...")
            response = self.gemini_model.generate_content("Say 'Connected' in one word only.")
            print(f"✅ API test successful: {response.text}")
            
            self.gemini_available = True
            print("🎉 Google Gemini fully configured and ready!")
            
        except Exception as e:
            print(f"❌ Gemini setup failed: {str(e)}")
            import traceback
            print(f"🔍 Full error traceback: {traceback.format_exc()}")
            self.gemini_available = False
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini"""
        if not self.gemini_available or not self.gemini_model:
            error_msg = "❌ Google Gemini is not available. "
            if not GOOGLE_AVAILABLE:
                error_msg += "Package not installed."
            elif not self.gemini_model:
                error_msg += "Model not initialized."
            else:
                error_msg += "Please check the server logs."
            return error_msg
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            print("🤖 Sending analysis request to Gemini...")
            print(f"📝 Prompt length: {len(prompt)} characters")
            
            # Add safety settings to avoid blocks
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            print("✅ Analysis received successfully")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            
            # Provide more specific error messages
            if "quota" in error_msg.lower():
                return "❌ API quota exceeded. Please try again later or use a different API key."
            elif "API key" in error_msg or "key" in error_msg.lower() or "permission" in error_msg.lower():
                return f"❌ API key issue: The provided API key may be invalid or restricted. Please check your API key configuration."
            elif "safety" in error_msg.lower() or "blocked" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Please try different property details or simplify your input."
            elif "location" in error_msg.lower() or "region" in error_msg.lower():
                return "🌍 API not available in your region. Please check Gemini API availability in your location."
            else:
                return f"❌ Gemini API error: {error_msg}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt for Gemini"""
        return f"""
As a real estate investment expert, analyze this property investment opportunity:

PROPERTY DETAILS:
- Address: {property_data.get('address', 'Not specified')}
- {property_data.get('bedrooms', 0)} bedrooms, {property_data.get('bathrooms', 0)} bathrooms
- {property_data.get('square_feet', 0)} square feet
- Condition: {property_data.get('condition', 'Unknown')}
- Built in {property_data.get('year_built', 'Unknown')}
- Property Type: {property_data.get('property_type', 'Unknown')}
- Purchase Price: ${property_data.get('purchase_price', 0):,}

COMPARABLE PROPERTIES IN AREA:
{json.dumps(comps_data.get('comparables', []), indent=2)}

Please provide a comprehensive real estate investment analysis covering:

1. ESTIMATED RENTAL VALUE: Provide a monthly rental range in USD
2. GROSS RENTAL YIELD: Calculate and provide as a percentage
3. MARKET DEMAND: Assess as High/Medium/Low based on comparables
4. VALUE-ADD OPPORTUNITIES: List top 3 improvements that could increase value
5. FLIP POTENTIAL: Assess renovation and resale potential
6. INVESTMENT RECOMMENDATION: Overall assessment (Good/Fair/Poor investment)

Be concise, data-driven, and focus on financial metrics. Format your response in clear sections.
"""
    
    def extract_metrics(self, analysis_text):
        """Extract key metrics from AI analysis"""
        metrics = {
            'rental_value': 'See analysis',
            'yield': 'See analysis', 
            'demand': 'See analysis',
            'flip_potential': 'See analysis'
        }
        
        if not analysis_text or analysis_text.startswith("❌") or analysis_text.startswith("⚠️"):
            return metrics
        
        # Extract rental value
        rental_match = re.search(r'\$(\d{1,4}(?:,\d{3})*(?:\s*-\s*\$\d{1,4}(?:,\d{3})*)?)\s*(?:per month|monthly|rent)', analysis_text)
        if rental_match:
            metrics['rental_value'] = f"${rental_match.group(1)}/mo"
        else:
            # Look for rental ranges in different formats
            rental_match = re.search(r'(\$\d{1,4}(?:,\d{3})*\s*-\s*\$\d{1,4}(?:,\d{3})*)', analysis_text)
            if rental_match:
                metrics['rental_value'] = f"{rental_match.group(1)}/mo"
        
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
        for potential in ['Excellent', 'Strong', 'Good', 'Moderate', 'Fair', 'Poor']:
            if potential in analysis_text and any(word in analysis_text.lower() for word in ['flip', 'potential', 'candidate', 'investment']):
                metrics['flip_potential'] = potential
                break
        
        return metrics
