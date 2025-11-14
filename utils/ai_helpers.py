import os
import json
import re
import sys
import traceback

class PropertyAIAnalyzer:
    def __init__(self):
        self.gemini_available = False
        self.gemini_model = None
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize Google Gemini API"""
        print("🔧 Starting Gemini API setup...")
        
        # Test import first
        try:
            import google.generativeai as genai
            self.GOOGLE_AVAILABLE = True
            print("✅ google.generativeai imported successfully")
        except ImportError as e:
            self.GOOGLE_AVAILABLE = False
            print(f"❌ Google Generative AI import failed: {e}")
            print("💡 Try: pip install google-generativeai")
            return
        
        # API Key
        self.google_key = "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
        print(f"🔑 API Key: {self.google_key[:10]}...")
        
        if not self.google_key or self.google_key == "YOUR_API_KEY_HERE":
            print("❌ No valid API key provided")
            return
        
        try:
            # Configure API
            print("🔄 Configuring Gemini API...")
            genai.configure(api_key=self.google_key)
            print("✅ API configured")
            
            # Test with model listing
            print("📋 Listing available models...")
            try:
                models = genai.list_models()
                model_list = [model.name for model in models if 'gemini' in model.name.lower()]
                print(f"✅ Found {len(model_list)} Gemini models: {model_list}")
            except Exception as e:
                print(f"⚠️ Could not list models (might be permission issue): {e}")
            
            # Initialize model
            print("🚀 Initializing Gemini Pro model...")
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Model initialized")
            
            # Test connection
            print("🧪 Testing API connection...")
            response = self.gemini_model.generate_content(
                "Respond with only the word 'SUCCESS' if you can read this.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0.1
                )
            )
            
            if "SUCCESS" in response.text:
                print("✅ API test successful!")
                self.gemini_available = True
            else:
                print(f"⚠️ Unexpected test response: {response.text}")
                self.gemini_available = True  # Still mark as available if we got a response
                
        except Exception as e:
            print(f"❌ Gemini setup failed: {str(e)}")
            print("🔍 Full error traceback:")
            traceback.print_exc()
            self.gemini_available = False
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini"""
        if not self.gemini_available:
            return "❌ Google Gemini is not available. Please check the server logs for configuration details."
        
        if not self.gemini_model:
            return "❌ Gemini model not initialized properly."
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            print("🤖 Sending analysis request to Gemini...")
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1024,
                }
            )
            
            print("✅ Analysis received successfully")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            
            # Specific error handling
            if "quota" in error_msg.lower():
                return "❌ API quota exceeded. Please try again later or use a different API key."
            elif "API key" in error_msg or "key" in error_msg.lower() or "permission" in error_msg.lower():
                return "❌ Invalid API key or permissions issue. Please check your API key configuration."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Please try different property details."
            elif "location" in error_msg.lower() or "region" in error_msg.lower():
                return "🌍 API not available in your region. Please check Gemini API availability."
            elif "503" in error_msg or "500" in error_msg:
                return "🔧 Gemini API is temporarily unavailable. Please try again in a few minutes."
            else:
                return f"❌ Gemini API error: {error_msg}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt for Gemini"""
        return f"""
As a real estate investment expert, analyze this property:

PROPERTY DETAILS:
- Address: {property_data.get('address', 'Not specified')}
- {property_data.get('bedrooms', 0)} bed, {property_data.get('bathrooms', 0)} bath
- {property_data.get('square_feet', 0)} sqft
- Condition: {property_data.get('condition', 'Unknown')}
- Built: {property_data.get('year_built', 'Unknown')}
- Type: {property_data.get('property_type', 'Unknown')}
- Price: ${property_data.get('purchase_price', 0):,}

COMPARABLE PROPERTIES:
{json.dumps(comps_data.get('comparables', []), indent=2)}

Provide analysis covering:
1. ESTIMATED RENTAL VALUE: Monthly rental range
2. GROSS YIELD: Percentage based on price and estimated rent
3. MARKET DEMAND: High/Medium/Low
4. VALUE-ADD OPPORTUNITIES: Top 3 improvements
5. FLIP POTENTIAL: Good/Fair/Poor
6. INVESTMENT RECOMMENDATION: Overall assessment

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
        
        if not analysis_text or analysis_text.startswith("❌") or analysis_text.startswith("⚠️"):
            return metrics
        
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
        for potential in ['Excellent', 'Strong', 'Good', 'Moderate', 'Fair', 'Poor']:
            if potential in analysis_text and any(word in analysis_text.lower() for word in ['flip', 'potential', 'candidate']):
                metrics['flip_potential'] = potential
                break
        
        return metrics
