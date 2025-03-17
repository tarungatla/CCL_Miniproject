import os
import streamlit as st
from dotenv import load_dotenv
from auth.cognito_auth import CognitoAuth

# Load environment variables from .env
load_dotenv()

# Fetch Cognito Configuration from environment variables
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")  # Default to ap-south-1

def show_auth_ui():
    auth = CognitoAuth()
    
    st.title("📦 Inventory Management System")
    
    # Verify configuration
    config_valid, config_message = auth.verify_configuration()
    
    # Enhanced debug section
    if st.checkbox("Show Configuration"):
        st.write("Cognito Configuration:")
        st.write({
            "User Pool ID": COGNITO_USER_POOL_ID or "Not set",
            "Client ID": COGNITO_CLIENT_ID or "Not set",
            "Region": AWS_REGION,
            "Status": "✅ Valid" if config_valid else f"❌ Invalid: {config_message}"
        })
        
        if not config_valid:
            st.error("""
            Please ensure you have:
            1. Created a Cognito User Pool
            2. Created a User Pool Client
            3. Set the correct values in your .env file
            4. Configured the client to allow USER_PASSWORD_AUTH
            """)
            return

    # Ensure session state is initialized
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_token = None

    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    success, result = auth.sign_in(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_token = result['AccessToken']
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {result}")
                else:
                    st.error("⚠️ Please fill in all fields.")
    
    with tab2:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            new_username = st.text_input("Username")
            email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if new_username and email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("⚠️ Passwords do not match")
                    else:
                        success, message = auth.sign_up(new_username, new_password, email)
                        if success:
                            st.success("✅ Registration successful! Please check your email for verification.")
                        else:
                            st.error(f"❌ Registration failed: {message}")
                else:
                    st.error("⚠️ Please fill in all fields.") 
