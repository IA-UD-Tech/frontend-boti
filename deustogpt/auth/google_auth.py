"""
google_auth.py
DeustoGPT

This module provides functions for handling Google OAuth authentication in Streamlit applications.
Created by Diego Revilla on 03/03/2025
"""

import os
import time
import base64
import json
import streamlit as st
import requests
from google_auth_oauthlib.flow import Flow

from deustogpt.config import OAUTH_REDIRECT_URI, DEUSTO_DOMAIN, OPENDEUSTO_DOMAIN


def login_with_google(intended_role : str):
    """
    Inicia el flujo de OAuth con Google.
    
    Args:
        intended_role: Role the user intends to login as ("teacher" or "student")
    """
    try:
        st.session_state.intended_role = intended_role
        flow = Flow.from_client_secrets_file(
            'client_secrets.json',
            scopes=["https://www.googleapis.com/auth/userinfo.profile", 
                    "https://www.googleapis.com/auth/userinfo.email", "openid"],
            redirect_uri=OAUTH_REDIRECT_URI
        )
        auth_url, state = flow.authorization_url(
            prompt='consent', 
            access_type='offline',
            state=os.urandom(16).hex()
        )
        st.session_state.google_oauth_state = state
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}" />', unsafe_allow_html=True)
        st.stop()
    except Exception as e:
        st.error(f"Error al iniciar sesión con Google: {str(e)}")
        return False


def handle_oauth_callback(query_params):
    """
    Process OAuth callback from Google.
    
    Args:
        query_params: Query parameters from the callback URL
    
    Returns:
        bool: True if authentication was successful, False otherwise
    """
    if "code" not in query_params:
        return False
        
    try:
        # Get the code - handle both list and single value cases
        if isinstance(query_params["code"], list):
            code = query_params["code"][0]
        else:
            code = query_params["code"]

        st.write(f"DEBUG: Received auth code (first 5 chars): {code[:5]}...")

        flow = Flow.from_client_secrets_file(
            'client_secrets.json',
            scopes=["https://www.googleapis.com/auth/userinfo.profile", 
                    "https://www.googleapis.com/auth/userinfo.email", "openid"],
            redirect_uri=OAUTH_REDIRECT_URI
        )

        # Exchange the authorization code for credentials
        token_data = flow.fetch_token(code=code)
        st.write("DEBUG: Token exchange successful")

        # Save the token
        st.session_state.google_token = flow.credentials.token

        # Get user info and assign role based on email domain
        user_info = get_user_info(flow.credentials.token)
        if user_info and "email" in user_info:
            email = user_info["email"]
            st.session_state.user_email = email
            
            # Assign role based on email domain
            if email.endswith(DEUSTO_DOMAIN):
                st.session_state.user_role = "teacher"
            elif email.endswith(OPENDEUSTO_DOMAIN):
                st.session_state.user_role = "student"
            else:
                st.error(f"Correo no autorizado. Solo se permiten dominios {DEUSTO_DOMAIN} y {OPENDEUSTO_DOMAIN}")
                st.session_state.google_token = None
                return False

        # Clear query parameters
        try:
            st.query_params.clear()
        except:
            st.experimental_set_query_params()

        st.success("¡Autenticación exitosa! Redirigiendo...")
        time.sleep(1)  # Brief pause before redirect
        st.rerun()
        return True

    except Exception as e:
        st.error(f"Error procesando el callback de Google: {str(e)}")
        st.write("Detalles del error:", str(e))

        # If there was an auth code issue, clear it to allow a fresh attempt
        try:
            st.query_params.clear()
        except:
            st.experimental_set_query_params()
        return False


def get_user_info(token):
    """
    Get user information from Google using the provided token.
    
    Args:
        token: Google OAuth token
        
    Returns:
        dict: User information
    """
    if not token:
        return None
        
    try:
        # First try to use it as a JWT token
        segments = token.split('.')
        if len(segments) == 3:
            # Looks like a JWT, try to decode it
            payload = segments[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 else ''
            decoded_payload = base64.b64decode(payload).decode('utf-8')
            return json.loads(decoded_payload)
        
        # If it's not a JWT, use it as an access token to call userinfo endpoint
        headers = {"Authorization": f"Bearer {token}"}
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo", 
            headers=headers
        )
        
        if userinfo_response.status_code == 200:
            return userinfo_response.json()
        else:
            st.error(f"Error al obtener información del usuario: {userinfo_response.text}")
            return None
                
    except Exception as e:
        st.error(f"Error al procesar el token de Google: {str(e)}")
        return None


def get_user_id():
    """
    Get a unique identifier for the current authenticated user.
    
    Returns:
        str: Unique user ID or None if not authenticated
    """
    token = st.session_state.google_token
    user_info = get_user_info(token)
    if user_info:
        return user_info.get("sub") or user_info.get("email")
    return None


def logout():
    """
    Log out the current user by clearing session state.
    """
    st.session_state.google_token = None
    st.session_state.user_email = None
    st.session_state.user_role = None
    st.rerun()