import os
import json
import re
import sys
import traceback

class PropertyAIAnalyzer:
    def __init__(self):
        self.gemini_available = False
        self.openai_available = False
        self.gemini_model = None
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize AI APIs with fallback"""
        print("🚀 STARTING AI API SETUP")
        
        # Try Gemini first
        self.setup_gemini()
        
        # If Gemini fails, try OpenAI
        if not self.gemini_available:
            self.setup_openai()
    
    def setup_gemini(self):
        """Setup Google Gemini"""
        try:
            import google.generativeai as genai
            print("✅ Google Generative AI package available")
            
            # Try multiple API keys
            api_keys = [
                "AIzaSyDA1gKnB7WwNiOwa7mzw0Wn7vJHK1t6YVg",
                "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
            ]
            
            for api_key in api_keys:
                try:
                    print(f"🔑 Trying API key: {api_key[:10]}...")
                    genai.configure(api_key=api_key)
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    
                    # Test the connection
                    response = self.gemini_model.generate_content("Test")
                    print("✅ Gemini API working!")
                    self.gemini_available = True
                    self.google_key = api_key
                    break
                    
                except Exception as e:
                    print(f"❌ API key failed: {e}")
                    continue
            
            if not self.gemini_available:
                print("❌ All Gemini API keys failed")
                
        except ImportError as e:
            print(f"❌ Gemini import failed: {e}")
    
    def setup_openai(self):
        """Setup OpenAI as fallback"""
        try:
            from openai import OpenAI
            print("🔄 Trying OpenAI as fallback...")
            
            # You would need to set OPENAI_API_KEY in your environment
            self.openai_client = OpenAI()
            self.openai_available = True
            print("✅ OpenAI available (will need API key)")
            
        except ImportError:
            print("❌ OpenAI not available")
        except Exception as e:
            print(f"❌ OpenAI setup failed: {e}")
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using available AI"""
        if self.gemini_available:
            return self._analyze_with_gemini(property_data, comps_data)
        elif self.openai_available:
            return self._analyze_with_openai(property_data, comps_data)
        else:
            return "❌ No AI services are currently available. Please check the API configuration."
    
    def _analyze_with_gemini(self, property_data, comps_data):
        """Analyze using Gemini"""
        try:
            prompt = self._create_analysis_prompt(property_data, comps_data)
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 800,
                }
            )
            return response.text
        except Exception as e:
            return f"❌ Gemini analysis failed: {str(e)}"
    
    def _analyze_with_openai(self, property_data, comps_data):
        """Analyze using OpenAI"""
        try:
            prompt = self._create_analysis_prompt(property_data, comps_data)
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ OpenAI analysis failed: {str(e)}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt"""
        return f"""
As a real estate investment expert, analyze this property:

PROPERTY:
- {property_data.get('bedrooms', 0)} bed, {property_data.get('bathrooms', 0)} bath
- {property_data.get('square_feet', 0)} sqft, {property_data.get('condition', 'Unknown')} condition
- Built in {property_data.get('year_built', 'Unknown')}
- Purchase price: ${property_data.get('purchase_price', 0):,}
- Type: {property_data.get('property_type', 'Unknown')}

COMPARABLES:
{json.dumps(comps_data.get('comparables', []), indent=2)}

Provide analysis covering:
1. Estimated monthly rental value
2. Gross rental yield percentage
3. Market demand level (High/Medium/Low)
4. Investment recommendation

Be concise and data-driven.
"""
    
    def extract_metrics(self, analysis_text):
        """Extract key metrics from analysis"""
        metrics = {
            'rental_value': 'See analysis',
            'yield': 'See analysis', 
            'demand': 'See analysis',
            'flip_potential': 'See analysis'
        }
        
        if not analysis_text or analysis_text.startswith("❌"):
            return metrics
        
        # Simple extraction
        try:
            if '$' in analysis_text:
                rental_match = re.search(r'\$(\d{1,4}(?:,\d{3})*)\s*(?:per month|monthly)', analysis_text)
                if rental_match:
                    metrics['rental_value'] = f"${rental_match.group(1)}/mo"
            
            yield_match = re.search(r'(\d+\.?\d*)%\s*(?:yield|return)', analysis_text, re.IGNORECASE)
            if yield_match:
                metrics['yield'] = f"{yield_match.group(1)}%"
            
            for level in ['High', 'Medium', 'Low']:
                if level in analysis_text and 'demand' in analysis_text.lower():
                    metrics['demand'] = level
                    break
                    
        except Exception:
            pass
        
        return metrics
