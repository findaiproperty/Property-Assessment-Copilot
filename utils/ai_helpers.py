import os
import openai
import google.generativeai as genai
from openai import OpenAI
import json
import re

class PropertyAIAnalyzer:
    def __init__(self):
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize all available AI APIs"""
        # OpenAI setup
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Google Gemini setup
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
    
    def analyze_with_openai(self, property_data, comps_data):
        """Analyze property using OpenAI"""
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using cheaper model
                messages=[
                    {"role": "system", "content": "You are a expert real estate analyst. Provide detailed, data-driven analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI analysis failed: {str(e)}"
    
    def analyze_with_gemini(self, property_data, comps_data):
        """Analyze property using Google Gemini"""
        if not self.gemini_model:
            return "Gemini API not configured"
        
        prompt = self._create_analysis_prompt(property_data, comps_data)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini analysis failed: {str(e)}"
    
    def _create_analysis_prompt(self, property_data, comps_data):
        """Create comprehensive analysis prompt"""
        return f"""
        Analyze this property for investment potential:

        PROPERTY DETAILS:
        {json.dumps(property_data, indent=2)}

        COMPARABLE PROPERTIES:
        {json.dumps(comps_data, indent=2)}

        Please provide a comprehensive analysis with:
        1. Rental Value Estimate (monthly range)
        2. Gross Rental Yield calculation
        3. Demand Assessment (High/Medium/Low)
        4. 3-5 suggested improvements to increase value
        5. Flip potential assessment with reasoning
        6. Overall investment recommendation

        Be data-driven and reference the comparable properties in your analysis.
        """
    
    def extract_metrics(self, analysis_text):
        """Extract key metrics from AI analysis for display"""
        metrics = {
            'rental_value': 'Not specified',
            'yield': 'Not specified',
            'demand': 'Not specified',
            'flip_potential': 'Not specified'
        }
        
        # Simple regex extraction (you can make this more sophisticated)
        rental_match = re.search(r'(\$\d{1,4}(?:,\d{3})*(?:-\$\d{1,4}(?:,\d{3})*)?\s*per month)', analysis_text)
        if rental_match:
            metrics['rental_value'] = rental_match.group(1)
        
        yield_match = re.search(r'(\d+\.?\d*%\s*yield)', analysis_text, re.IGNORECASE)
        if yield_match:
            metrics['yield'] = yield_match.group(1)
        
        demand_match = re.search(r'(High|Medium|Low)\s+[Dd]emand', analysis_text)
        if demand_match:
            metrics['demand'] = demand_match.group(1)
        
        flip_match = re.search(r'(Strong|Moderate|Poor)\s+[Ff]lip', analysis_text)
        if flip_match:
            metrics['flip_potential'] = flip_match.group(1)
        
        return metrics

# Free API key management
def get_free_apis():
    """Instructions for getting free API keys"""
    return {
        "OpenAI": "Get $5 free credit at https://platform.openai.com",
        "Google Gemini": "Free tier available at https://makersuite.google.com",
        "Hugging Face": "Free inference API at https://huggingface.co"
    }
