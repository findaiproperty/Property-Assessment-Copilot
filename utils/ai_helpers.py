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
        """Initialize Google Gemini API with better error handling"""
        print("🚀 STARTING GEMINI SETUP")
        
        # Test import first
        try:
            import google.generativeai as genai
            self.GOOGLE_AVAILABLE = True
            print("✅ google.generativeai imported successfully")
        except ImportError as e:
            self.GOOGLE_AVAILABLE = False
            print(f"❌ Google Generative AI import failed: {e}")
            self.gemini_available = False
            return
        
        # Try multiple API keys with better error handling
        api_keys = [
            "AIzaSyDA1gKnB7WwNiOwa7mzw0Wn7vJHK1t6YVg",
            "AIzaSyBFcWY9PUlf4T7cudtkPpLD7lhwM5lNIEk"
        ]
        
        for i, api_key in enumerate(api_keys):
            try:
                print(f"🔑 Trying API key {i+1}: {api_key[:10]}...")
                
                # Configure API
                genai.configure(api_key=api_key)
                print("✅ API configured")
                
                # Initialize model
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                print("✅ Model initialized")
                
                # Simple test with timeout handling
                import time
                start_time = time.time()
                response = self.gemini_model.generate_content(
                    "Hello! Respond with just 'OK'.",
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=10,
                        temperature=0.1
                    )
                )
                
                elapsed_time = time.time() - start_time
                print(f"✅ Test response: '{response.text}' (took {elapsed_time:.2f}s)")
                
                self.gemini_available = True
                self.google_key = api_key
                print("🎉 GEMINI SETUP COMPLETE AND WORKING!")
                break
                
            except Exception as e:
                print(f"❌ API key {i+1} failed: {str(e)}")
                continue
        
        if not self.gemini_available:
            print("❌ All Gemini API keys failed")
            # Provide detailed debug info
            print("🔧 DEBUG INFO:")
            print(f"- Python path: {sys.path}")
            print(f"- Current dir: {os.getcwd()}")
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini with enhanced error handling"""
        if not self.gemini_available or not self.gemini_model:
            error_msg = "❌ AI service is currently unavailable. "
            error_msg += "This could be due to API quota limits or configuration issues. "
            error_msg += "Please try again later or contact support."
            return error_msg
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            print("🤖 Sending analysis request to Gemini...")
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "max_output_tokens": 800,
                }
            )
            
            print("✅ Analysis received successfully")
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            
            # More specific error handling
            if "quota" in error_msg.lower():
                return "❌ API quota exceeded. The free tier has limited requests. Please try again in a few hours."
            elif "API key" in error_msg.lower() or "key" in error_msg.lower():
                return "❌ API key authentication failed. Please check if the API key is valid."
            elif "safety" in error_msg.lower():
                return "⚠️ Content blocked by safety filters. Please adjust your property description."
            elif "503" in error_msg or "500" in error_msg:
                return "🔧 Gemini API is temporarily unavailable. Please try again in a few minutes."
            else:
                return f"❌ Analysis failed: {error_msg}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create analysis prompt for Gemini"""
        comps_text = ""
        for i, comp in enumerate(comps_data.get('comparables', [])):
            comps_text += f"Comp {i+1}: ${comp.get('price', 0):,} | Rent: ${comp.get('rent', 0):,}/mo | {comp.get('sqft', 0)} sqft\n"
        
        return f"""
As a real estate investment expert, analyze this property investment opportunity:

**PROPERTY DETAILS:**
- Address: {property_data.get('address', 'Not specified')}
- {property_data.get('bedrooms', 0)} bed, {property_data.get('bathrooms', 0)} bath
- {property_data.get('square_feet', 0)} sqft, {property_data.get('condition', 'Unknown')} condition
- Built: {property_data.get('year_built', 'Unknown')}, Type: {property_data.get('property_type', 'Unknown')}
- Purchase Price: ${property_data.get('purchase_price', 0):,}

**COMPARABLE PROPERTIES:**
{comps_text if comps_text else 'No comparables provided'}

Please provide a concise investment analysis covering:
1. **Estimated Rental Value**: What monthly rent could this property command?
2. **Gross Rental Yield**: Calculate (Annual Rent / Purchase Price) as percentage
3. **Market Demand**: High/Medium/Low based on property type and location
4. **Investment Recommendation**: Good/Fair/Poor opportunity and brief reasoning

Keep response under 300 words and focus on actionable insights.
"""
    
    def extract_metrics(self, analysis_text):
        """Extract key metrics from AI analysis with improved pattern matching"""
        metrics = {
            'rental_value': 'See analysis',
            'yield': 'See analysis', 
            'demand': 'See analysis',
            'flip_potential': 'See analysis'
        }
        
        if not analysis_text or analysis_text.startswith("❌"):
            return metrics
        
        try:
            # Look for rental value patterns
            rental_patterns = [
                r'\$(\d{1,4}(?:,\d{3})*)\s*(?:per month|monthly|rent)',
                r'rent.*?\$(\d{1,4}(?:,\d{3})*)',
                r'\$(\d{1,4}(?:,\d{3})*).*?(?:month|rent)'
            ]
            
            for pattern in rental_patterns:
                rental_match = re.search(pattern, analysis_text, re.IGNORECASE)
                if rental_match:
                    metrics['rental_value'] = f"${rental_match.group(1)}/mo"
                    break
            
            # Look for yield percentage
            yield_patterns = [
                r'(\d+\.?\d*)%\s*(?:yield|return)',
                r'yield.*?(\d+\.?\d*)%',
                r'return.*?(\d+\.?\d*)%'
            ]
            
            for pattern in yield_patterns:
                yield_match = re.search(pattern, analysis_text, re.IGNORECASE)
                if yield_match:
                    metrics['yield'] = f"{yield_match.group(1)}%"
                    break
            
            # Look for demand level
            demand_keywords = ['high', 'medium', 'low']
            for level in demand_keywords:
                if re.search(rf'\b{level}\b.*?demand', analysis_text, re.IGNORECASE):
                    metrics['demand'] = level.title()
                    break
            
            # Look for investment potential
            potential_keywords = ['excellent', 'strong', 'good', 'fair', 'poor', 'great', 'decent']
            for potential in potential_keywords:
                if re.search(rf'\b{potential}\b', analysis_text, re.IGNORECASE):
                    if potential in ['great', 'decent']:
                        metrics['flip_potential'] = 'Good'
                    else:
                        metrics['flip_potential'] = potential.title()
                    break
                    
        except Exception as e:
            print(f"Metric extraction error: {e}")
        
        return metrics
