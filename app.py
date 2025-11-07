import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
from utils.auth import AuthSystem
from utils.ai_helpers import PropertyAIAnalyzer, get_free_apis

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
    tab1, tab2, tab3 = st.sidebar.tabs(["Login", "Register", "API Setup"])
    
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
    
    with tab3:
        st.subheader("Free API Setup")
        st.info("Get free API keys to power the AI analysis:")
        apis = get_free_apis()
        for name, info in apis.items():
            st.write(f"**{name}**: {info}")
        
        st.subheader("Configure Your Keys")
        openai_key = st.text_input("OpenAI API Key", type="password")
        google_key = st.text_input("Google API Key", type="password")
        
        if st.button("Save API Keys"):
            # In production, store these securely
            os.environ['OPENAI_API_KEY'] = openai_key
            os.environ['GOOGLE_API_KEY'] = google_key
            st.success("API keys configured for this session!")

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
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
    
    # Main application
    st.title("🏠 Property AI Analyzer")
    st.write("Get AI-powered analysis of property investment opportunities")
    
    # Check usage limits
    if not auth_system.check_usage_limit(st.session_state.username):
        st.error("""
        🚫 **Usage Limit Reached**
        
        You've used all your free analyses for this month. Please upgrade to premium for unlimited access.
        """)
        show_upgrade_modal()
        return
    
    # Property input form
    with st.form("property_analysis_form"):
        st.subheader("Property Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_input("Property Address")
            bedrooms = st.number_input("Bedrooms", min_value=0, max_value=10, value=3)
            bathrooms = st.number_input("Bathrooms", min_value=0, max_value=10, value=2, step=0.5)
            sqft = st.number_input("Square Feet", min_value=0, value=1500)
        
        with col2:
            property_type = st.selectbox("Property Type", ["Single Family", "Condo", "Townhouse", "Multi-Family"])
            year_built = st.number_input("Year Built", min_value=1800, max_value=2024, value=1990)
            purchase_price = st.number_input("Purchase Price ($)", min_value=0, value=300000)
            condition = st.selectbox("Condition", ["Excellent", "Good", "Fair", "Poor"])
        
        st.subheader("Comparable Properties")
        st.write("Add at least 2 comparable properties in the area:")
        
        comps = []
        for i in range(3):
            col1, col2, col3 = st.columns(3)
            with col1:
                comp_price = st.number_input(f"Comp {i+1} Price", min_value=0, value=300000, key=f"comp_price_{i}")
            with col2:
                comp_rent = st.number_input(f"Comp {i+1} Rent", min_value=0, value=2000, key=f"comp_rent_{i}")
            with col3:
                comp_sqft = st.number_input(f"Comp {i+1} SqFt", min_value=0, value=1500, key=f"comp_sqft_{i}")
            comps.append({"price": comp_price, "rent": comp_rent, "sqft": comp_sqft})
        
        ai_provider = st.selectbox("AI Provider", ["OpenAI GPT-3.5", "Google Gemini"])
        
        if st.form_submit_button("🚀 Analyze Property"):
            with st.spinner("AI is analyzing your property..."):
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
                
                # Perform analysis
                if ai_provider == "OpenAI GPT-3.5":
                    analysis = ai_analyzer.analyze_with_openai(property_data, comps_data)
                else:
                    analysis = ai_analyzer.analyze_with_gemini(property_data, comps_data)
                
                # Increment usage
                auth_system.increment_usage(st.session_state.username)
                
                # Display results
                st.success("Analysis Complete!")
                
                # Extract and display key metrics
                metrics = ai_analyzer.extract_metrics(analysis)
                
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
                
                # Visualizations
                st.subheader("📈 Market Comparison")
                create_comparison_charts(comps, purchase_price)

def create_comparison_charts(comps, purchase_price):
    """Create comparison charts"""
    df = pd.DataFrame(comps)
    df['comp'] = [f'Comp {i+1}' for i in range(len(comps))]
    
    # Price comparison
    fig_price = px.bar(
        x=['Your Property'] + df['comp'].tolist(),
        y=[purchase_price] + df['price'].tolist(),
        title="Price Comparison",
        labels={'x': 'Properties', 'y': 'Price ($)'}
    )
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Rent comparison
    if 'rent' in df.columns:
        fig_rent = px.bar(
            x=df['comp'],
            y=df['rent'],
            title="Rental Price Comparison",
            labels={'x': 'Comparable Properties', 'y': 'Monthly Rent ($)'}
        )
        st.plotly_chart(fig_rent, use_container_width=True)

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
