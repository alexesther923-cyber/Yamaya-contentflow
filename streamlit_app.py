
import streamlit as st
import tempfile
import os

from gemini_generator import generate_content_ideas
from editorial_review import review_content
from contentflow_pipeline import run_contentflow_pipeline
from output_formatter import save_generated_content
from streamlit_url_fragments import get_fragments
from urllib.parse import parse_qs

st.set_page_config(
    page_title="Yamaya ContentFlow",
    page_icon="✍️",
    layout="centered"
)

from auth import (
    login,
    logout,
    send_password_recovery,
    complete_password_recovery,
    get_platform_role
)
# Password recovery screen
# Password recovery
fragments = get_fragments()

recovery_data = {}

if isinstance(fragments, dict):
    recovery_data = fragments

elif isinstance(fragments, str):
    recovery_data = {
        key: values[0]
        for key, values in parse_qs(
            fragments.lstrip("#?")
        ).items()
    }

access_token = recovery_data.get("access_token")
refresh_token = recovery_data.get("refresh_token")
recovery_type = recovery_data.get("type")

if (
    access_token
    and refresh_token
    and recovery_type == "recovery"
    and not st.session_state.get("recovery_completed")
):
    st.title("YAMAYA CONTENTFLOW")
    st.subheader("Reset your password")

    new_password = st.text_input(
        "New password",
        type="password"
    )

    confirm_password = st.text_input(
        "Confirm new password",
        type="password"
    )

    if st.button("Update password"):
        if len(new_password) < 8:
            st.warning("Password must be at least 8 characters.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            try:
                complete_password_recovery(
                    access_token,
                    refresh_token,
                    new_password
                )

                st.session_state["recovery_completed"] = True
                st.success("Password updated successfully!")
                st.rerun()

            except Exception:
                st.error(
                    "Password reset failed. Request a fresh recovery email."
                )

    st.stop()
# Authentication gate
if not st.session_state.get("authenticated", False):
    st.title("YAMAYA CONTENTFLOW")
    st.subheader("Sign in to your account")

    email = st.text_input("Email address")
    password = st.text_input("Password", type="password")

    if st.button("Forgot password?"):
        if email.strip():
            try:
                send_password_recovery(email)
                st.success("If your account exists, a recovery email will be sent.")
            except Exception:
                st.error("Could not request password recovery. Try again later.")
        else:
            st.warning("Enter your email address first.")

    if st.button("Sign in"):
        if email.strip() and password:
            try:
                login(email, password)
                st.success("Login successful!")
                st.rerun()
            except Exception:
                st.error("Login failed. Check your email and password.")
        else:
            st.warning("Enter your email and password.")

    st.stop()
# Load platform role
platform_role = get_platform_role()
st.session_state["platform_role"] = platform_role
st.sidebar.write("Your platform role:", platform_role)
# Logged-in user controls
st.sidebar.write(
    f"Signed in as: {st.session_state.get('user_email', '')}"
)

if st.sidebar.button("Log out"):
    logout()
    st.rerun()


st.title("YAMAYA CONTENTFLOW")
st.caption("AI-powered content planning, editorial review and repurposing.")

brand_name = st.sidebar.selectbox(
    "Select Brand",
    ["Yamaya Afrique", "ErikaL Naturals"]
)

workflow = st.sidebar.selectbox(
    "Choose Workflow",
    [
        "Content Ideation",
        "Editorial Review",
        "Content Repurposing Studio"
    ]
)

st.divider()

if workflow == "Content Ideation":

    st.subheader("Generate Content")

    topic = st.text_input("Content topic")
    audience = st.text_input("Target audience")
    format_type = st.selectbox("Content format", ["Reel", "Carousel"])
    tone = st.text_input("Preferred tone", "Engaging and relatable")

    if st.button("Generate Content", type="primary"):
        if not topic or not audience:
            st.warning("Please enter a topic and target audience.")
        else:
            with st.spinner("Generating content..."):
                try:
                    result = generate_content_ideas(
                        topic, audience, format_type, tone, brand_name
                    )
                    st.session_state["result"] = {
                        "Content Ideas": result
                    }
                except Exception as error:
                    st.error(f"Generation failed: {error}")

elif workflow == "Editorial Review":

    st.subheader("Review Existing Content")

    content = st.text_area(
        "Paste the content you want reviewed",
        height=250
    )

    if st.button("Review Content", type="primary"):
        if not content.strip():
            st.warning("Please paste content first.")
        else:
            with st.spinner("Reviewing content..."):
                try:
                    result = review_content(content, brand_name)
                    st.session_state["result"] = {
                        "Editorial Review": result
                    }
                except Exception as error:
                    st.error(f"Review failed: {error}")

elif workflow == "Content Repurposing Studio":

    st.subheader("Repurpose Existing Content")

    source_option = st.radio(
        "Choose your source",
        ["Paste text", "Upload a document or image"]
    )

    source_text = None
    file_path = None
    uploaded_file = None

    if source_option == "Paste text":
        source_text = st.text_area(
            "Paste your source material",
            height=250
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload PDF, DOCX or image",
            type=["pdf", "docx", "jpg", "jpeg", "png", "webp"]
        )

    output_formats = st.multiselect(
        "Choose output formats",
        [
            "Carousel",
            "Reel",
            "Blog Article",
            "Newsletter",
            "Social Media Caption"
        ]
    )

    if st.button("Repurpose Content", type="primary"):

        if source_option == "Paste text" and not source_text.strip():
            st.warning("Please paste your source material.")

        elif source_option == "Upload a document or image" and not uploaded_file:
            st.warning("Please upload a file.")

        elif not output_formats:
            st.warning("Please select at least one output format.")

        else:
            try:
                if uploaded_file:
                    suffix = os.path.splitext(uploaded_file.name)[1]

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix
                    ) as temp_file:
                        temp_file.write(uploaded_file.getvalue())
                        file_path = temp_file.name

                with st.spinner("Processing and repurposing content..."):
                    result = run_contentflow_pipeline(
                        brand_name=brand_name,
                        output_formats=output_formats,
                        source_text=source_text,
                        file_path=file_path
                    )

                st.session_state["result"] = result["generated_content"]

            except Exception as error:
                st.error(f"Repurposing failed: {error}")

            finally:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)


if "result" in st.session_state:

    st.divider()
    st.subheader("Your Content")

    for format_name, content in st.session_state["result"].items():
        with st.expander(format_name, expanded=True):
            st.write(content)

    if st.button("Prepare Word Document"):
        try:
            saved_files = save_generated_content(
                st.session_state["result"],
                brand_name
            )

            for path in saved_files:
                with open(path, "rb") as document:
                    st.download_button(
                        label="Download Word Document",
                        data=document.read(),
                        file_name=os.path.basename(path),
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

        except Exception as error:
            st.error(f"Document export failed: {error}")
