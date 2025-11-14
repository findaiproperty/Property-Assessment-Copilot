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
        print("🚀 STARTING GEMINI SETUP")
        
        # Test import
        try:
            import google.generativeai as genai
            self.GOOGLE_AVAILABLE = True
            print("✅ google.generativeai imported successfully")
        except ImportError as e:
            self.GOOGLE_AVAILABLE = False
            print(f"❌ Google Generative AI import failed: {e}")
            self.gemini_available = False
            return
        
        # API Key - Using a fresh key
        self.google_key = "AIzaSyDA1gKnB7WwNiOwa7mzw0Wn7vJHK1t6YVg"  # Fresh test key
        print(f"🔑 API Key configured: {self.google_key[:10]}...")
        
        if not self.google_key:
            print("❌ No API key provided")
            self.gemini_available = False
            return
        
        try:
            # Configure API
            print("🔄 Configuring Gemini API...")
            genai.configure(api_key=self.google_key)
            print("✅ API configured")
            
            # Initialize model
            print("🚀 Initializing Gemini Pro model...")
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Model initialized")
            
            # Simple test
            print("🧪 Testing API with simple request...")
            response = self.gemini_model.generate_content(
                "Hello! Respond with just 'OK' if you're working.",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=20,
                    temperature=0.1
                )
            )
            
            print(f"✅ Test response: {response.text}")
            self.gemini_available = True
            print("🎉 GEMINI SETUP COMPLETE AND WORKING!")
            
        except Exception as e:
            print(f"❌ SETUP FAILED: {str(e)}")
            print("🔍 FULL ERROR TRACEBACK:")
            traceback.print_exc()
            self.gemini_available = False
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini"""
        if not self.gemini_available or not self.gemini_model:
            return "❌ AI service is currently unavailable. Please try again later or contact support."
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            print("🤖 Sending analysis request to Gemini...")
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_output_tokens": 1000,
                }
            )
            
            print("✅ Analysis received successfully")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            
            if "quota" in error_msg.lower():
                return "❌ API quota exceeded. Please try again later."
            elif "API key" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API key issue. Please check the configuration."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters."
            else:
                return f"❌ Analysis failed: {error_msg}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt for Gemini"""
        return f"""
Please analyze this real estate investment property:

PROPERTY DETAILS:
- Address: {property_data.get('address', 'Not specified')}
- {property_data.get('bedrooms', 0)} bedrooms, {property_data.get('bathrooms', 0)} bathrooms
- {property_data.get('square_feet', 0)} square feet
- Condition: {property_data.get('condition', 'Unknown')}
- Year Built: {property_data.get('year_built', 'Unknown')}
- Property Type: {property_data.get('property_type', 'Unknown')}
- Purchase Price: ${property_data.get('purchase_price', 0):,}

COMPARABLE PROPERTIES:
{json.dumps(comps_data.get('comparables', []), indent=2)}

Please provide a concise analysis covering:
1. Estimated monthly rental value
2. Gross rental yield percentage
3. Market demand assessment (High/Medium/Low)
4. Investment potential

Keep the response under 500 words and focus on key metrics.
"""
    
    def extract_metrics(self, analysis_text):
        """Extract key metrics from AI analysis"""
        metrics = {
            'rental_value': 'See analysis',
            'yield': 'See analysis', 
            'demand': 'See analysis',
            'flip_potential': 'See analysis'
        }
        
        if not analysis_text or analysis_text.startswith("❌"):
            return metrics
        
        # Simple extraction logic
        try:
            # Look for rental value
            if '$' in analysis_text:
                rental_match = re.search(r'\$(\d{1,4}(?:,\d{3})*)\s*(?:per month|monthly|rent)', analysis_text)
                if rental_match:
                    metrics['rental_value'] = f"${rental_match.group(1)}/mo"
            
            # Look for yield percentage
            yield_match = re.search(r'(\d+\.?\d*)%\s*(?:yield|return)', analysis_text, re.IGNORECASE)
            if yield_match:
                metrics['yield'] = f"{yield_match.group(1)}%"
            
            # Look for demand level
            for level in ['High', 'Medium', 'Low']:
                if level in analysis_text and 'demand' in analysis_text.lower():
                    metrics['demand'] = level
                    break
            
            # Look for investment potential
            for potential in ['Excellent', 'Strong', 'Good', 'Fair', 'Poor']:
                if potential in analysis_text:
                    metrics['flip_potential'] = potential
                    break
                    
        except Exception as e:
            print(f"Metric extraction error: {e}")
        
        return metrics
