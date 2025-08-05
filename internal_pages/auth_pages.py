"""Authentication pages for login and signup with smooth CSS animations."""
import streamlit as st
from utils.auth import authenticate_user, create_user, login_user
from config import APP_NAME

def load_css():
    """Load custom CSS styles with enhanced animations."""
    try:
        with open('assets/styles.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styling.")
    
    # Enhanced CSS with smooth animations and larger tabs
    st.markdown("""
    <style>
    /* Logo Animation Keyframes - Truck and QuickDeliver slide from right to center */
    @keyframes truckMove {
        0% {
            opacity: 0;
            transform: translateX(300px);
        }
        100% {
            opacity: 1;
            transform: translateX(0px);
        }
    }
    
    @keyframes quickDeliverMove {
        0% {
            opacity: 0;
            transform: translateX(200px);
        }
        100% {
            opacity: 1;
            transform: translateX(0px);
        }
    }
    
    @keyframes taglineMove {
        0% {
            opacity: 0;
            transform: translateX(150px);
        }
        100% {
            opacity: 1;
            transform: translateX(0px);
        }
    }
    
    /* Form Container Animations */
    @keyframes slideInFromBottom {
        0% {
            opacity: 0;
            transform: translateY(50px);
        }
        100% {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInScale {
        0% {
            opacity: 0;
            transform: scale(0.9);
        }
        100% {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes shimmer {
        0% {
            background-position: -200% 0;
        }
        100% {
            background-position: 200% 0;
        }
    }
    
    /* Main Header Styling */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem;
        animation: fadeInScale 1s ease-out forwards;
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        color: #333;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.2rem;
        color: #666;
        opacity: 0;
        animation: taglineMove 2s ease-out 1s forwards;
    }
    
    /* Logo Animation Elements */
    #truck-anim {
        display: inline-block;
        font-size: 2rem;
        animation: truckMove 2.5s ease-out forwards;
        opacity: 0;
    }
    
    #quickdeliver-anim {
        display: inline-block;
        animation: quickDeliverMove 2.5s ease-out 0.5s forwards;
        opacity: 0;
    }    
    /* Form Container */
    .login-container {
        background: transparent;
        padding: 0;
        animation: slideInFromBottom 1s ease-out 0.8s forwards;
        opacity: 0;
        transform: translateY(50px);
    }
    
    /* Enhanced Tab Styling - Much Larger Buttons WITHOUT Background Box */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        background: transparent !important;
        border-radius: 0px !important;
        padding: 8px 0px !important;
        margin-bottom: 2rem !important;
        box-shadow: none !important;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 16px !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 600 !important;
        font-size: 1.2rem !important;
        padding: 16px 32px !important;
        min-height: 60px !important;
        min-width: 140px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: rgba(248, 250, 252, 0.8) !important;
        color: #666 !important;
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        cursor: pointer !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stTabs [data-baseweb="tab"]:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2) !important;
        border-color: rgba(102, 126, 234, 0.3) !important;
        color: #667eea !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover:before {
        left: 100%;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-2px) scale(1.05) !important;
        border-color: #667eea !important;
        font-weight: 700 !important;
    }
    
    .stTabs [aria-selected="true"]:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%) !important;
        transform: translateY(-4px) scale(1.06) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.6) !important;
    }
    
    /* Tab Content Animation */
    .stTabs [data-baseweb="tab-panel"] {
        animation: fadeInScale 0.5s ease-out;
        padding-top: 1rem;
    }
    
    /* Input Field Animations - FIXED: Consistent styling for all textboxes */
    .stTextInput > div > div > input,
    .stTextInput input,
    [data-testid="textInput-rootElement"] input,
    [data-baseweb="input"] input {
        border: 2px solid rgba(102, 126, 234, 0.2) !important;
        border-radius: 10px !important;
        padding: 16px 20px !important;
        background: rgba(248, 250, 252, 0.8) !important;
        transition: all 0.3s ease !important;
        font-size: 16px !important;
        outline: none !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        min-height: 50px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextInput input:focus,
    [data-testid="textInput-rootElement"] input:focus,
    [data-baseweb="input"] input:focus {
        border-color: #667eea !important;
        background: white !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), 0 4px 15px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-2px) !important;
    }
    
    .stTextInput > label {
        font-weight: 600 !important;
        color: #4a5568 !important;
        margin-bottom: 8px !important;
        font-size: 1rem !important;
    }
    
    /* Button Animations - FIXED: Adjusted margin to prevent border cut-off */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 16px 32px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        color: white !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
        min-height: 50px !important;
        width: 100% !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        margin: 2px 2px 2px 8px !important;
    }
    
    .stButton > button:before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
        background: linear-gradient(135deg, #5a67d8 0%, #667eea 100%) !important;
    }
    
    .stButton > button:hover:before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Alert/Message Animations */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        animation: slideInFromBottom 0.5s ease-out !important;
        margin: 16px 0 !important;
        padding: 16px 20px !important;
        font-weight: 500 !important;
    }
    
    .stSuccess {
        background: linear-gradient(135deg, #6BCF7F 0%, #4D9F56 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(107, 207, 127, 0.3) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, #FF6B6B 0%, #CC5555 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(78, 205, 196, 0.3) !important;
    }
    
    /* Form Animation */
    .stForm {
        animation: fadeInScale 0.6s ease-out;
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
        background: rgba(255, 255, 255, 0.5);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Subheader Styling */
    .stMarkdown h3 {
        color: #333 !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        text-align: center !important;
        font-size: 1.8rem !important;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
            flex-direction: column;
            gap: 0.2rem;
        }
        
        .login-container {
            margin: 1rem;
            padding: 1.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 1rem !important;
            padding: 12px 24px !important;
            min-width: 120px !important;
            min-height: 50px !important;
        }
    }
    
    /* Loading Animation for Demo Info */
    .demo-info {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        animation: slideInFromBottom 0.8s ease-out;
    }
    
    .demo-info:after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
        animation: shimmer 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)

def login_page():
    """Display login/signup page with animations."""
    load_css()
    
    # Animated header with logo transition from right to center
    st.markdown(f"""
    <div class="main-header">
        <h1>
            <div id="truck-anim">🚚</div>
            <div id="quickdeliver-anim">{APP_NAME}</div>
        </h1>
        <p>Your favorite food, delivered fast</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Sign In", "📝 Sign Up"])
        
        with tab1:
            signin_form()
        
        with tab2:
            signup_form()
            
        st.markdown('</div>', unsafe_allow_html=True)

def signin_form():
    """Display sign in form - UNCHANGED FUNCTIONALITY."""
    st.subheader("Welcome Back!")
    
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
    
    # st.markdown('<div class="demo-info">', unsafe_allow_html=True)
    # st.info("💡 Demo credentials: Username: *demo, Password: **password*")
    # st.markdown('</div>', unsafe_allow_html=True)

def signup_form():
    """Display sign up form - UNCHANGED FUNCTIONALITY."""
    st.subheader("Join QuickDeliver")
    
    with st.form("signup_form"):
        new_username = st.text_input("👤 Choose Username", key="signup_username", placeholder="Choose a unique username")
        new_name = st.text_input("🏷 Full Name", key="signup_name", placeholder="Enter your full name")
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