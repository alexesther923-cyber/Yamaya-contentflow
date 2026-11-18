
import streamlit as st
from supabase import create_client
from supabase_auth import SyncSupportedStorage
from supabase.lib.client_options import SyncClientOptions
import hashlib
import json
import secrets
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet

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
    st.session_state["user_id"] = str(response.user.id)
    st.session_state["auth_access_token"] = response.session.access_token
    st.session_state["auth_refresh_token"] = response.session.refresh_token

    return response


def get_platform_role():
    supabase = get_supabase()

    user_id = st.session_state.get("user_id")

    if not user_id:
        return None

    response = (
        supabase.table("platform_roles")
        .select("role")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    if response.data:
        return response.data["role"]

    return None
def get_platform_users():
    supabase = get_supabase()

    response = supabase.rpc(
        "get_platform_users"
    ).execute()

    return response.data or []
def get_brands():
    supabase = get_supabase()

    response = (
        supabase.table("brands")
        .select("id, name, description")
        .order("name")
        .execute()
    )

    return response.data or []
def create_brand(brand_name, brand_description):
    supabase = get_supabase()

    response = supabase.rpc(
        "create_brand",
        {
            "brand_name": brand_name,
            "brand_description": brand_description
        }
    ).execute()

    return response.data
def get_brand_profile_data(brand_name):
    supabase = get_supabase()

    response = (
        supabase.table("brands")
        .select("*")
        .eq("name", brand_name)
        .single()
        .execute()
    )

    return response.data

def update_brand_profile(brand_id, profile_data):
    supabase = get_supabase()

    response = (
        supabase.table("brands")
        .update(profile_data)
        .eq("id", brand_id)
        .execute()
    )

    return response.data
def assign_platform_role(user_id, role):
    supabase = get_supabase()

    return supabase.rpc(
        "assign_platform_role",
        {
            "target_user_id": user_id,
            "new_role": role
        }
    ).execute()
def send_password_recovery(email):
    supabase = get_supabase()

    return supabase.auth.reset_password_for_email(
        email.strip().lower(),
        {"redirect_to": APP_URL}
    )


def complete_password_recovery(access_token, refresh_token, new_password):
    supabase = get_supabase()

    response = supabase.auth.set_session(
        access_token,
        refresh_token
    )

    supabase.auth.update_user({
        "password": new_password
    })

    st.session_state["authenticated"] = True
    st.session_state["user_email"] = response.user.email
    st.session_state["user_id"] = str(response.user.id)
    st.session_state["auth_access_token"] = response.session.access_token
    st.session_state["auth_refresh_token"] = response.session.refresh_token

    return response


def logout():
    supabase = get_supabase()
    supabase.auth.sign_out()

    for key in [
        "authenticated",
        "user_email",
        "user_id",
        "auth_access_token",
        "auth_refresh_token",
        "supabase_client",
        "login_email",
        "recovery_completed"
    ]:
        st.session_state.pop(key, None)
        
SESSION_COOKIE = "yamaya_session"
SESSION_TIMEOUT_MINUTES = 30
SESSION_MAX_DAYS = 30


def _get_fernet():
    key = st.secrets["SESSION_ENCRYPTION_KEY"]
    return Fernet(key.encode())


def _hash_session(token):
    return hashlib.sha256(token.encode()).hexdigest()


def _encrypt_session(access_token, refresh_token):
    data = json.dumps({
        "access_token": access_token,
        "refresh_token": refresh_token
    }).encode()

    return _get_fernet().encrypt(data).decode()


def _read_session_record(session_hash):
    result = get_supabase().rpc(
        "get_app_session",
        {"p_session_token_hash": session_hash}
    ).execute()

    data = result.data

    if isinstance(data, list):
        return data[0] if data else None

    return data if isinstance(data, dict) else None


def _clear_persistent_login(cookie_manager, session_hash=None):
    if session_hash:
        try:
            get_supabase().rpc(
                "revoke_app_session",
                {"p_session_token_hash": session_hash}
            ).execute()
        except Exception:
            pass

    try:
        cookie_manager.delete(SESSION_COOKIE)
    except Exception:
        pass

    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass

    for key in [
        "authenticated",
        "user_email",
        "user_id",
        "auth_access_token",
        "auth_refresh_token",
        "persistent_session_hash",
        "platform_role"
    ]:
        st.session_state.pop(key, None)


def create_persistent_session(cookie_manager):
    access_token = st.session_state["auth_access_token"]
    refresh_token = st.session_state["auth_refresh_token"]

    token = secrets.token_urlsafe(32)
    session_hash = _hash_session(token)

    encrypted = _encrypt_session(
        access_token,
        refresh_token
    )

    expires = (
        datetime.now(timezone.utc)
        + timedelta(days=SESSION_MAX_DAYS)
    )

    get_supabase().rpc(
        "create_app_session",
        {
            "p_session_token_hash": session_hash,
            "p_encrypted_session": encrypted,
            "p_expires_at": expires.isoformat()
        }
    ).execute()

    cookie_manager.set(
        SESSION_COOKIE,
        token,
        max_age=SESSION_MAX_DAYS * 86400,
        secure=True,
        same_site="strict"
    )

    st.session_state["persistent_session_hash"] = session_hash


def restore_persistent_session(cookie_manager):
    token = cookie_manager.get(SESSION_COOKIE)

    if not token:
        return False

    session_hash = _hash_session(token)
    record = _read_session_record(session_hash)

    if not record:
        cookie_manager.delete(SESSION_COOKIE)
        return False

    last_activity = datetime.fromisoformat(
        record["last_activity_at"].replace("Z", "+00:00")
    )

    idle_time = (
        datetime.now(timezone.utc) - last_activity
    )

    if idle_time > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        _clear_persistent_login(cookie_manager, session_hash)
        return False

    try:
        encrypted = record["encrypted_session"].encode()
        saved = json.loads(
            _get_fernet().decrypt(encrypted).decode()
        )
    except Exception:
        _clear_persistent_login(cookie_manager, session_hash)
        return False

    response = get_supabase().auth.set_session(
        saved["access_token"],
        saved["refresh_token"]
    )

    if not response.session:
        return False

    if str(response.user.id) != str(record["user_id"]):
        _clear_persistent_login(cookie_manager, session_hash)
        return False

    session = response.session

    st.session_state["authenticated"] = True
    st.session_state["user_email"] = response.user.email
    st.session_state["user_id"] = str(response.user.id)
    st.session_state["auth_access_token"] = session.access_token
    st.session_state["auth_refresh_token"] = session.refresh_token
    st.session_state["persistent_session_hash"] = session_hash

    updated_encrypted = _encrypt_session(
        session.access_token,
        session.refresh_token
    )

    get_supabase().rpc(
        "update_app_session",
        {
            "p_session_token_hash": session_hash,
            "p_encrypted_session": updated_encrypted
        }
    ).execute()

    get_supabase().rpc(
        "touch_app_session",
        {"p_session_token_hash": session_hash}
    ).execute()

    return True


def check_session_timeout(cookie_manager):
    session_hash = st.session_state.get(
        "persistent_session_hash"
    )

    if not session_hash:
        return True

    record = _read_session_record(session_hash)

    if not record:
        _clear_persistent_login(cookie_manager)
        return False

    last_activity = datetime.fromisoformat(
        record["last_activity_at"].replace("Z", "+00:00")
    )

    if (
        datetime.now(timezone.utc) - last_activity
        > timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    ):
        _clear_persistent_login(cookie_manager, session_hash)
        return False

    get_supabase().rpc(
        "touch_app_session",
        {"p_session_token_hash": session_hash}
    ).execute()

    return True


def logout_persistent(cookie_manager):
    session_hash = st.session_state.get(
        "persistent_session_hash"
    )

    if not session_hash:
        token = cookie_manager.get(SESSION_COOKIE)
        if token:
            session_hash = _hash_session(token)

    _clear_persistent_login(cookie_manager, session_hash)
    st.session_state.pop("supabase_client", None)
def save_content_draft(brand_id, workflow, draft_data):
    supabase = get_supabase()

    response = supabase.table("content_drafts").upsert(
        {
            "user_id": st.session_state["user_id"],
            "brand_id": brand_id,
            "workflow": workflow,
            "draft_data": draft_data,
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        on_conflict="user_id,brand_id,workflow"
    ).execute()

    return response.data


def get_content_draft(brand_id, workflow):
    supabase = get_supabase()

    response = (
        supabase.table("content_drafts")
        .select("draft_data")
        .eq("user_id", st.session_state["user_id"])
        .eq("brand_id", brand_id)
        .eq("workflow", workflow)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]["draft_data"]

    return {}
def delete_content_draft(brand_id, workflow):
    supabase = get_supabase()

    return (
        supabase.table("content_drafts")
        .delete()
        .eq("user_id", st.session_state["user_id"])
        .eq("brand_id", brand_id)
        .eq("workflow", workflow)
        .execute()
    )
def save_saved_content_draft(brand_id, title, workflow, draft_data):
    supabase = get_supabase()

    response = supabase.table("saved_content_drafts").insert({
        "user_id": st.session_state["user_id"],
        "brand_id": brand_id,
        "title": title,
        "workflow": workflow,
        "draft_data": draft_data
    }).execute()

    return response.data


def get_saved_content_drafts(brand_id=None):
    supabase = get_supabase()

    query = (
        supabase.table("saved_content_drafts")
        .select("*")
        .eq("user_id", st.session_state["user_id"])
        .order("updated_at", desc=True)
    )

    if brand_id:
        query = query.eq("brand_id", brand_id)

    response = query.execute()

    return response.data or []


def get_saved_content_draft(draft_id):
    supabase = get_supabase()

    response = (
        supabase.table("saved_content_drafts")
        .select("*")
        .eq("id", draft_id)
        .eq("user_id", st.session_state["user_id"])
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return {}


def delete_saved_content_draft(draft_id):
    supabase = get_supabase()

    return (
        supabase.table("saved_content_drafts")
        .delete()
        .eq("id", draft_id)
        .eq("user_id", st.session_state["user_id"])
        .execute()
    )
def create_working_draft(brand_id, workflow, title="Untitled Draft"):
    supabase = get_supabase()

    response = supabase.table("working_drafts").insert({
        "user_id": st.session_state["user_id"],
        "brand_id": brand_id,
        "workflow": workflow,
        "title": title,
        "draft_data": {},
        "generated_result": {},
        "status": "open"
    }).execute()

    return response.data


def get_working_drafts(brand_id, workflow):
    supabase = get_supabase()

    response = (
        supabase.table("working_drafts")
        .select("*")
        .eq("user_id", st.session_state["user_id"])
        .eq("brand_id", brand_id)
        .eq("workflow", workflow)
        .order("updated_at", desc=True)
        .execute()
    )

    return response.data or []


def update_working_draft(draft_id, draft_data, generated_result=None, title=None):
    supabase = get_supabase()

    update_data = {
        "draft_data": draft_data,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    if generated_result is not None:
        update_data["generated_result"] = generated_result

    if title is not None:
        update_data["title"] = title

    response = (
        supabase.table("working_drafts")
        .update(update_data)
        .eq("id", draft_id)
        .eq("user_id", st.session_state["user_id"])
        .execute()
    )

    return response.data


def set_working_draft_status(draft_id, status):
    supabase = get_supabase()

    response = (
        supabase.table("working_drafts")
        .update({
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("id", draft_id)
        .eq("user_id", st.session_state["user_id"])
        .execute()
    )

    return response.data


def delete_working_draft(draft_id):
    supabase = get_supabase()

    response = (
        supabase.table("working_drafts")
        .delete()
        .eq("id", draft_id)
        .eq("user_id", st.session_state["user_id"])
        .execute()
    )

    return response.data
