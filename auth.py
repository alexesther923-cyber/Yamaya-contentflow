
import streamlit as st
from supabase import create_client


def get_supabase():
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
    return st.session_state.supabase_client


def login(email, password):
    supabase = get_supabase()

    response = supabase.auth.sign_in_with_password({
        "email": email.strip().lower(),
        "password": password
    })

    st.session_state["authenticated"] = True
    st.session_state["user_email"] = response.user.email
    st.session_state["auth_access_token"] = response.session.access_token
    st.session_state["auth_refresh_token"] = response.session.refresh_token

    return response


def logout():
    supabase = get_supabase()
    supabase.auth.sign_out()

    for key in [
        "authenticated",
        "user_email",
        "auth_access_token",
        "auth_refresh_token",
        "supabase_client",
        "login_email"
    ]:
        st.session_state.pop(key, None)
