import streamlit as st
import json
import os
from datetime import datetime
import pandas as pdf
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import AuthSystem
from ai_helpers import PropertyAIAnalyzer

# Page configuration
st.set_page_config(
    page_title="Property AI Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize systems
@st.cache_resource
def get_auth_system():
    return AuthSystem()

@st.cache_resource  
def get_ai_analyzer():
    return PropertyAIAnalyzer()

auth_system = get_auth_system()
ai_analyzer = get_ai_analyzer()

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    # Sidebar for authentication
    st.sidebar.title("🔐 Authentication")
    
    if not st.session_state.authenticated:
        show_auth_interface()
    else:
        show_main_application()

def show_auth_interface():
    """Show login/register interface"""
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", key="login_btn"):
            if login_username and login_password:
                with st.spinner("Logging in..."):
                    success, message = auth_system.verify_user(login_username, login_password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.username = login_username
                        st.rerun()
                    else:
                        st.error(f"Login failed: {message}")
            else:
                st.warning("Please enter both username and password")
    
    with tab2:
        st.subheader("Create Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register", key="register_btn"):
            if reg_username and reg_email and reg_password and reg_confirm:
                if reg_password != reg_confirm:
                    st.error("Passwords don't match")
                else:
                    with st.spinner("Creating account..."):
                        success, message = auth_system.create_user(reg_username, reg_password, reg_email)
                        if success:
                            st.success("✅ Account created successfully! Please login with your new account.")
                            st.rerun()
                        else:
                            st.error(f"Registration failed: {message}")
            else:
                st.warning("Please fill in all fields")

def show_main_application():
    """Show the main application after login"""
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    
    # User info
    user_plan = auth_system.get_user_plan(st.session_state.username)
    remaining_uses = auth_system.users[st.session_state.username]['max_uses'] - auth_system.users[st.session_state.username]['usage_count']
    
    st.sidebar.write(f"**Plan**: {user_plan.upper()}")
    if user_plan == 'free':
        st.sidebar.write(f"**Remaining Analyses**: {remaining_uses}/5")
    
    # AI Service Status
    if ai_analyzer.gemini_available:
        st.sidebar.success("✅ AI Service Ready")
    else:
        st.sidebar.error("❌ AI Service Unavailable")
        st.sidebar.write("Please check the deployment logs for errors")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    # Main application
    st.title("🏠 Property AI Analyzer")
    st.write("Get instant AI-powered analysis of property investment opportunities using Google Gemini")
    
    # Check usage limits
    if not auth_system.check_usage_limit(st.session_state.username):
        st.error("""
        🚫 **Usage Limit Reached**
        
        You've used all your free analyses for this month. 
        """)
        return
    
    # Check if Gemini is configured
    if not ai_analyzer.gemini_available:
        st.error("""
        🔧 **AI Service Configuration Issue**
        
        The AI service is currently unavailable. This is being investigated.
        """)
        # Show debug info
        with st.expander("Technical Details"):
            st.write("**API Status:**")
            st.write(f"- Gemini Available: {ai_analyzer.gemini_available}")
            st.write(f"- Package Installed: {hasattr(ai_analyzer, 'GOOGLE_AVAILABLE') and ai_analyzer.GOOGLE_AVAILABLE}")
            if hasattr(ai_analyzer, 'google_key'):
                st.write(f"- API Key Configured: {bool(ai_analyzer.google_key)}")
                if ai_analyzer.google_key:
                    st.write(f"- Key Preview: {ai_analyzer.google_key[:10]}...")
        return
    
    # Property input form
    with st.form("property_analysis_form"):
        st.subheader("Property Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_input("Property Address", placeholder="123 Main Street, City, State")
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3)
            bathrooms = st.number_input("Bathrooms", min_value=0, max_value=10, value=2, step=0.5)
            sqft = st.number_input("Square Feet", min_value=0, value=1500)
        
        with col2:
            property_type = st.selectbox("Property Type", ["Single Family", "Condo", "Townhouse", "Multi-Family"])
            year_built = st.number_input("Year Built", min_value=1800, max_value=2024, value=1990)
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=300000)
            condition = st.selectbox("Condition", ["Excellent", "Good", "Fair", "Poor", "Needs Renovation"])
        
        st.subheader("Comparable Properties")
        st.write("Add 2-3 comparable properties in the area:")
        
        comps = []
        for i in range(3):
            st.write(f"**Comparable Property {i+1}:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                comp_price = st.number_input(f"Sale Price", min_value=0, value=300000, key=f"comp_price_{i}")
            with col2:
                comp_rent = st.number_input(f"Monthly Rent", min_value=0, value=2000, key=f"comp_rent_{i}")
            with col3:
                comp_sqft = st.number_input(f"Square Feet", min_value=0, value=1500, key=f"comp_sqft_{i}")
            comps.append({"price": comp_price, "rent": comp_rent, "sqft": comp_sqft})
        
        if st.form_submit_button("🚀 Analyze Property with AI"):
            with st.spinner("Google Gemini is analyzing your property..."):
                # Prepare data
                property_data = {
                    "address": address,
                    "bedrooms": bedrooms,
                    "bathrooms": bathrooms,
                    "square_feet": sqft,
                    "property_type": property_type,
                    "year_built": year_built,
                    "purchase_price": purchase_price,
                    "condition": condition
                }
                
                comps_data = {"comparables": comps}
                
                # Perform analysis with Gemini
                analysis = ai_analyzer.analyze_with_gemini(property_data, comps_data)
                
                # Increment usage
                auth_system.increment_usage(st.session_state.username)
                
                # Display results
                st.success("Analysis Complete! ✅")
                
                # Extract and display key metrics
                metrics = ai_analyzer.extract_metrics(analysis)
                
                st.subheader("📈 Quick Insights")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Estimated Rental Value", metrics['rental_value'])
                with col2:
                    st.metric("Gross Yield", metrics['yield'])
                with col3:
                    st.metric("Demand Level", metrics['demand'])
                with col4:
                    st.metric("Flip Potential", metrics['flip_potential'])
                
                # Display full analysis
                st.subheader("📊 Detailed Analysis")
                st.write(analysis)
                
                # Market comparison
                create_comparison_charts(comps, purchase_price)

def create_comparison_charts(comps, purchase_price):
    """Create simple comparison tables"""
    st.subheader("📊 Market Comparison")
    
    # Price comparison table
    price_data = {
        'Property': ['Your Property'] + [f'Comp {i+1}' for i in range(len(comps))],
        'Price': [f"${purchase_price:,}"] + [f"${comp['price']:,}" for comp in comps],
        'Monthly Rent': ['N/A'] + [f"${comp.get('rent', 'N/A'):,}" for comp in comps],
        'Price per SqFt': [f"${purchase_price/comps[0]['sqft']:,.0f}" if comps and comps[0]['sqft'] > 0 else 'N/A'] + 
                         [f"${comp['price']/comp['sqft']:,.0f}" if comp['sqft'] > 0 else 'N/A' for comp in comps]
    }
    
    price_df = pd.DataFrame(price_data)
    st.dataframe(price_df, use_container_width=True, hide_index=True)
    
    # Market insights
    st.subheader("💡 Market Insights")
    if comps:
        avg_comp_price = sum(comp['price'] for comp in comps) / len(comps)
        price_difference = purchase_price - avg_comp_price
        price_percentage = (price_difference / avg_comp_price) * 100
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Comp Price", f"${avg_comp_price:,.0f}")
        with col2:
            st.metric("Price vs Market", f"${price_difference:,.0f}", f"{price_percentage:+.1f}%")
        with col3:
            if any(comp.get('rent') for comp in comps):
                valid_rents = [comp.get('rent', 0) for comp in comps if comp.get('rent', 0) > 0]
                if valid_rents:
                    avg_rent = sum(valid_rents) / len(valid_rents)
                    st.metric("Avg Monthly Rent", f"${avg_rent:,.0f}")

if __name__ == "__main__":
    main()
