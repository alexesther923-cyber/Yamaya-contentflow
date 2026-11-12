
import streamlit as st
import tempfile
import os

from gemini_generator import generate_content_ideas
from editorial_review import review_content
from contentflow_pipeline import run_contentflow_pipeline
from output_formatter import save_generated_content


st.set_page_config(
    page_title="Yamaya ContentFlow",
    page_icon="✍️",
    layout="centered"
)

from auth import send_login_code, verify_login_code, logout

# Authentication gate
if not st.session_state.get("authenticated", False):

    st.title("YAMAYA CONTENTFLOW")
    st.subheader("Sign in")

    email = st.text_input("Email address")

    if st.button("Send verification code"):
        if email.strip():
            try:
                send_login_code(email)
                st.session_state["login_email"] = email.strip().lower()
                st.success("Verification code sent. Check your email.")
            except Exception as e:
                st.error(f"Could not send code: {e}")
        else:
            st.warning("Enter your email address.")

    if st.session_state.get("login_email"):
        code = st.text_input(
            "Enter your 6-digit verification code",
            max_chars=6
        )

        if st.button("Verify and sign in"):
            try:
                verify_login_code(
                    st.session_state["login_email"],
                    code
                )
                st.success("Signed in successfully!")
                st.rerun()
            except Exception:
                st.error("Invalid or expired code. Please try again.")

    st.stop()

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
