import streamlit as st
from supabase import create_client


def get_supabase():
    """Create or retrieve the user's Supabase client."""

    if "supabase_client" not in st.session_state:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]

        st.session_state.supabase_client = create_client(
            url,
            key
        )

    return st.session_state.supabase_client


def send_login_code(email):
    """Send a verification code to an existing user."""

    supabase = get_supabase()

    return supabase.auth.sign_in_with_otp({
        "email": email.strip().lower(),
        "options": {
            "should_create_user": False
        }
    })


def verify_login_code(email, code):
    """Verify the email code and sign the user in."""

    supabase = get_supabase()

    response = supabase.auth.verify_otp({
        "email": email.strip().lower(),
        "token": code.strip(),
        "type": "email"
    })

    if response.session:
        st.session_state["auth_access_token"] = (
            response.session.access_token
        )
        st.session_state["auth_refresh_token"] = (
            response.session.refresh_token
        )
        st.session_state["authenticated"] = True
        st.session_state["user_email"] = (
            response.user.email
        )

    return response


def logout():
    """Sign out the current user."""

    supabase = get_supabase()
    supabase.auth.sign_out()

    for key in [
        "authenticated",
        "auth_access_token",
        "auth_refresh_token",
        "user_email",
        "supabase_client"
    ]:
        st.session_state.pop(key, None)
