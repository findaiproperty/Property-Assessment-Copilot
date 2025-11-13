import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from utils.auth import AuthSystem
from utils.ai_helpers import PropertyAIAnalyzer

# Page configuration
st.set_page_config(
    page_title="Property AI Analyzer",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize systems
auth_system = AuthSystem()
ai_analyzer = PropertyAIAnalyzer()

def main():
    # Sidebar for authentication
    st.sidebar.title("🔐 Authentication")
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    
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
        
        if st.button("Login"):
            success, message = auth_system.verify_user(login_username, login_password)
            if success:
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error(message)
    
    with tab2:
        st.subheader("Create Account")
        reg_username = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        
        if st.button("Register"):
            if reg_password != reg_confirm:
                st.error("Passwords don't match")
            else:
                success, message = auth_system.create_user(reg_username, reg_password, reg_email)
                if success:
                    st.success("Account created! Please login.")
                else:
                    st.error(message)

def show_main_application():
    """Show the main application after login"""
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    
    # User info and upgrade
    user_plan = auth_system.get_user_plan(st.session_state.username)
    remaining_uses = auth_system.users[st.session_state.username]['max_uses'] - auth_system.users[st.session_state.username]['usage_count']
    
    st.sidebar.write(f"**Plan**: {user_plan.upper()}")
    if user_plan == 'free':
        st.sidebar.write(f"**Remaining Analyses**: {remaining_uses}/5")
        if st.sidebar.button("🚀 Upgrade to Premium"):
            show_upgrade_modal()
    
    # Check if Gemini is configured
    if ai_analyzer.gemini_available:
        st.sidebar.success("✅ AI Service Ready")
    else:
        st.sidebar.error("❌ AI Service Unavailable")
        st.sidebar.info("Please check API key configuration in Streamlit secrets")
    
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
        
        You've used all your free analyses for this month. Please upgrade to premium for unlimited access.
        """)
        show_upgrade_modal()
        return
    
    # Check if Gemini is configured
    if not ai_analyzer.gemini_available:
        st.error("""
        🔧 **Service Configuration Required**
        
        The AI service is not properly configured. Please contact the administrator.
        """)
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

def show_upgrade_modal():
    """Show upgrade options"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🚀 Upgrade to Premium")
    st.sidebar.write("**Unlock unlimited property analyses:**")
    st.sidebar.write("✅ Unlimited AI analyses")
    st.sidebar.write("✅ Advanced analytics")
    st.sidebar.write("✅ Historical data")
    st.sidebar.write("✅ Priority support")
    
    if st.sidebar.button("Upgrade Now - $29/month"):
        # In a real app, this would integrate with Stripe/PayPal
        auth_system.upgrade_user(st.session_state.username, 'premium')
        st.sidebar.success("Upgraded to Premium!")
        st.rerun()

if __name__ == "__main__":
    main()
