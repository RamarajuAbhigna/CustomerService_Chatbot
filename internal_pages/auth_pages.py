"""Authentication pages for login and signup."""

import streamlit as st
from utils.auth import authenticate_user, create_user, login_user
from config import APP_NAME


def login_page():
    """Display login/signup page."""
    # Simple and clean CSS for auth pages
    st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    
    /* Main container */
    .auth-container {
        background: white;
        border-radius: 20px;
        padding: 3rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid #e1e5e9;
        margin: 2rem auto;
        max-width: 700px;
        min-height: 500px;
    }
    
    /* Header styling */
    .auth-header {
        text-align: center;
        margin-bottom: 3rem;
        padding-bottom: 1.5rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .auth-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        font-size: 3rem;
        font-weight: 700;
        color: #333;
        margin-bottom: 1rem;
    }
    
    .auth-logo .truck-icon {
        font-size: 3.5rem;
        color: #667eea;
    }
    
    .auth-subtitle {
        color: #666;
        font-size: 1.3rem;
        margin: 0;
    }
    
    /* Form container */
    .form-container {
        max-width: 400px;
        margin: 0 auto;
    }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 2px solid #e1e5e9 !important;
        padding: 1rem 1.2rem !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
        background: white !important;
        height: 50px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput > label {
        color: #333 !important;
        font-weight: 600 !important;
        margin-bottom: 0.8rem !important;
        font-size: 0.95rem !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        margin-top: 1rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: #f8f9fa;
        border-radius: 15px;
        padding: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        background: transparent !important;
        color: #666 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    /* Demo info styling */
    .demo-info {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1.5rem;
        text-align: center;
        color: #155724;
    }
    
    .demo-info strong {
        color: #0d4b14;
    }
    
    .demo-info code {
        background: rgba(13, 75, 20, 0.1);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: monospace;
        font-weight: 600;
    }
    
    /* Form section titles */
    .form-section-title {
        color: #333;
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* Error and success messages */
    .stAlert {
        border-radius: 8px !important;
        margin: 1rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main container
    #st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div class="auth-header">
        <div class="auth-logo">
            <span class="truck-icon">🚚</span>
            <span>QuickDeliver</span>
        </div>
        <p class="auth-subtitle">Your favorite food, delivered fast</p>
    </div>
    """, unsafe_allow_html=True)

    # Tabs for Sign In and Sign Up
    tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])

    with tab1:
        signin_form()

    with tab2:
        signup_form()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close auth-container


def signin_form():
    """Display sign in form."""
    st.markdown("""
    <div class="form-container">
        <div class="form-section-title">👋 Welcome Back!</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("signin_form"):
        username = st.text_input("👤 Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("🔒 Password", type="password", key="login_password", placeholder="Enter your password")

        submit_button = st.form_submit_button("🚀 Sign In")

        if submit_button:
            if not username or not password:
                st.error("❌ Please fill in all fields")
            elif authenticate_user(username, password):
                login_user(username)
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")

    # st.markdown("""
    #     <div class="demo-info">
    #         <strong>💡 Demo Account</strong><br>
    #         Username: <code>demo</code> | Password: <code>password</code>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)


def signup_form():
    """Display sign up form."""
    st.markdown("""
    <div class="form-container">
        <div class="form-section-title">🎉 Join QuickDeliver</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("signup_form"):
        new_username = st.text_input("👤 Choose Username", key="signup_username", placeholder="Choose a unique username")
        new_name = st.text_input("🏷️ Full Name", key="signup_name", placeholder="Enter your full name")
        new_email = st.text_input("📧 Email Address", key="signup_email", placeholder="Enter your email address")
        new_password = st.text_input("🔒 Password", type="password", key="signup_password", placeholder="Create a strong password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", key="confirm_password", placeholder="Confirm your password")

        submit_button = st.form_submit_button("🎯 Create Account")

        if submit_button:
            if not all([new_username, new_name, new_email, new_password, confirm_password]):
                st.error("❌ Please fill in all fields")
            elif new_password != confirm_password:
                st.error("❌ Passwords don't match")
            elif len(new_password) < 6:
                st.error("❌ Password must be at least 6 characters")
            elif "@" not in new_email or "." not in new_email:
                st.error("❌ Please enter a valid email address")
            elif len(new_username) < 3:
                st.error("❌ Username must be at least 3 characters")
            elif len(new_name.strip()) < 2:
                st.error("❌ Please enter your full name")
            elif create_user(new_username, new_email, new_password, new_name):
                st.success("✅ Account created successfully! Please sign in with your new credentials.")
                st.balloons()
            else:
                st.error("❌ Username or email already exists. Please try different credentials.")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close form-container