
import streamlit as st
from supabase import create_client
from supabase_auth import SyncSupportedStorage
from supabase.lib.client_options import SyncClientOptions


APP_URL = "https://yamaya-contentflow.streamlit.app"


class StreamlitSessionStorage(SyncSupportedStorage):

    def get_item(self, key):
        return st.session_state.get(f"sb:{key}")

    def set_item(self, key, value):
        st.session_state[f"sb:{key}"] = value

    def remove_item(self, key):
        st.session_state.pop(f"sb:{key}", None)


def get_supabase():
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"],
            options=SyncClientOptions(
                flow_type="pkce",
                storage=StreamlitSessionStorage(),
                persist_session=False,
                auto_refresh_token=False
            )
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


def send_password_recovery(email):
    supabase = get_supabase()

    return supabase.auth.reset_password_for_email(
        email.strip().lower(),
        {"redirect_to": APP_URL}
    )


def complete_password_recovery(code, new_password):
    supabase = get_supabase()

    response = supabase.auth.exchange_code_for_session({
        "auth_code": code
    })

    supabase.auth.update_user({
        "password": new_password
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
