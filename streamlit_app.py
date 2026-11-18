
import streamlit as st
import tempfile
import os
import extra_streamlit_components as stx

from gemini_generator import generate_content_ideas
from editorial_review import review_content
from contentflow_pipeline import run_contentflow_pipeline
from output_formatter import save_generated_content
from streamlit_url_fragments import get_fragments
from urllib.parse import parse_qs

from auth import (
    login,
    logout,
    send_password_recovery,
    complete_password_recovery,
    get_platform_role,
    get_platform_users,
    assign_platform_role,
    get_brands,
    create_brand,
    get_brand_profile_data,
    update_brand_profile,
    create_persistent_session,
    restore_persistent_session,
    check_session_timeout,
    logout_persistent,
    create_working_draft,
    get_working_drafts,
    update_working_draft,
    set_working_draft_status,
    delete_working_draft,
    save_content_draft,
    get_content_draft,
    delete_content_draft,
    save_saved_content_draft,
    get_saved_content_drafts,
    get_saved_content_draft,
    delete_saved_content_draft,
)
st.set_page_config(
    page_title="Yamaya ContentFlow",
    page_icon="✍️",
    layout="centered"
)

cookie_manager = stx.CookieManager(
    key="yamaya_cookie_manager"
)
# PASSWORD RECOVERY
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

# RESTORE PERSISTENT LOGIN
if not st.session_state.get("authenticated", False):
    try:
        restored = restore_persistent_session(cookie_manager)
    except Exception as error:
        st.error(f"Session restore error: {error}")
# AUTHENTICATION GATE
if not st.session_state.get("authenticated", False):

    st.title("YAMAYA CONTENTFLOW")
    st.subheader("Sign in to your account")

    email = st.text_input("Email address")
    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Forgot password?"):

        if email.strip():
            try:
                send_password_recovery(email)

                st.success(
                    "If your account exists, a recovery email will be sent."
                )

            except Exception:
                st.error(
                    "Could not request password recovery. Try again later."
                )

        else:
            st.warning("Enter your email address first.")

    if st.button("Sign in"):

        if email.strip() and password:
            try:
                login(email, password)
                create_persistent_session(cookie_manager)

                st.success("Login successful!")
                st.rerun()

            except Exception as error:
                st.error(f"Login failed: {error}")

        else:
            st.warning("Enter your email and password.")
    st.stop()
if not check_session_timeout(cookie_manager):
    st.warning("Your session expired after inactivity. Please sign in again.")
    st.rerun()
# LOAD PLATFORM ROLE
platform_role = get_platform_role()
st.session_state["platform_role"] = platform_role

# LOGGED-IN USER CONTROLS
st.sidebar.write(
    f"Signed in as: {st.session_state.get('user_email', '')}"
)

st.sidebar.write(
    "Your platform role:",
    platform_role
)

if st.sidebar.button("Log out"):
    logout_persistent(cookie_manager)
    st.rerun()

# MAIN DASHBOARD
st.title("YAMAYA CONTENTFLOW")

st.caption(
    "AI-powered content planning, editorial review and repurposing."
)

# BRAND SELECTION
try:
    available_brands = get_brands()
    brand_names = [brand["name"] for brand in available_brands]

    if brand_names:
        brand_name = st.sidebar.selectbox(
            "Select Brand",
            brand_names
        )

        selected_brand_id = next(
            brand["id"]
            for brand in available_brands
            if brand["name"] == brand_name
        )

    else:
        brand_name = None
        selected_brand_id = None
        st.sidebar.warning("No brands available.")

except Exception as error:
    brand_name = None
    selected_brand_id = None
    st.sidebar.error(f"Could not load brands: {error}")


# WORKFLOW MENU
workflow_options = [
    "Content Ideation",
    "Editorial Review",
    "Content Repurposing Studio",
    "My Drafts"
]

if platform_role == "platform_owner":
    workflow_options.append("Platform Administration")
if "pending_workflow" in st.session_state:
    st.session_state["workflow_selector"] = (
        st.session_state.pop("pending_workflow")
    )
workflow = st.sidebar.selectbox(
    "Choose Workflow",
    workflow_options,
    key="workflow_selector"
)

st.divider()



# PLATFORM ADMINISTRATION
if workflow == "Platform Administration":

    st.subheader("Platform Owner Dashboard")

    st.write("Welcome to Yamaya ContentFlow administration.")

    # REGISTERED USERS
    st.markdown("### Registered Users")

    try:
        users = get_platform_users()

        if users:
            user_directory = []

            for user in users:
                user_directory.append({
                    "Name": user.get("display_name") or "Not provided",
                    "Email": user.get("email") or "Not available",
                    "Platform Role": user.get("platform_role") or "Unassigned",
                    "Date Joined": user.get("account_created_at") or "Unknown"
                })

            st.dataframe(
                user_directory,
                use_container_width=True,
                hide_index=True
            )

            st.caption(f"Total registered users: {len(users)}")

            # ROLE ASSIGNMENT
            st.divider()
            st.markdown("### Assign Platform Roles")

            available_users = [
                user for user in users
                if user.get("email")
            ]

            if available_users:

                selected_email = st.selectbox(
                    "Select a user",
                    [user["email"] for user in available_users]
                )

                selected_user = next(
                    user for user in available_users
                    if user["email"] == selected_email
                )

                current_role = selected_user.get("platform_role")

                if current_role == "platform_owner":

                    st.success(
                        "This account is the Platform Owner. "
                        "Its role cannot be changed here."
                    )

                else:

                    st.write(
                        f"Current role: {current_role or 'Unassigned'}"
                    )

                    role_options = [
                        "administrator",
                        "editor",
                        "contributor",
                        "viewer"
                    ]

                    selected_role = st.selectbox(
                        "Choose new role",
                        role_options
                    )

                    if st.button("Save Role", type="primary"):

                        try:
                            assign_platform_role(
                                selected_user["user_id"],
                                selected_role
                            )

                            st.success(
                                f"Role updated to {selected_role}."
                            )

                            st.rerun()

                        except Exception as error:
                            st.error(
                                f"Could not update role: {error}"
                            )

            else:
                st.info("No users with available email addresses.")

        else:
            st.info("No registered users found.")

    except Exception as error:
        st.error(f"Could not load users: {error}")



    # OTHER MANAGEMENT SECTIONS
    st.divider()
    st.markdown("### Brand Management")

    # CREATE BRAND
    with st.form("create_brand_form"):
        new_brand_name = st.text_input("Brand Name")
        new_brand_description = st.text_area(
            "Brand Description",
            placeholder="Describe what this brand does and stands for."
        )

        submit_brand = st.form_submit_button(
            "Create Brand",
            type="primary"
        )

        if submit_brand:
            if not new_brand_name.strip():
                st.error("Please enter a brand name.")
            else:
                try:
                    create_brand(
                        new_brand_name,
                        new_brand_description
                    )
                    st.success(
                        f"{new_brand_name} created successfully!"
                    )
                    st.rerun()
                except Exception as error:
                    st.error(f"Could not create brand: {error}")

    # EDIT BRAND PROFILE
    st.divider()
    st.markdown("### Edit Brand Profile")

    try:
        profile_brands = get_brands()
        profile_brand_names = [
            b["name"] for b in profile_brands
        ]

        if profile_brand_names:
            selected_profile_brand = st.selectbox(
                "Choose a brand to edit",
                profile_brand_names,
                key="profile_brand_selector"
            )

            profile = get_brand_profile_data(
                selected_profile_brand
            )

            with st.form("edit_brand_profile_form"):
                purpose = st.text_area(
                    "Brand Purpose",
                    value=profile.get("purpose") or ""
                )
                target_audience = st.text_area(
                    "Target Audience",
                    value=profile.get("target_audience") or ""
                )
                brand_values = st.text_area(
                    "Brand Values",
                    value=profile.get("brand_values") or ""
                )
                tone_of_voice = st.text_area(
                    "Tone of Voice",
                    value=profile.get("tone_of_voice") or ""
                )
                brand_personality = st.text_area(
                    "Brand Personality",
                    value=profile.get("brand_personality") or ""
                )
                content_pillars = st.text_area(
                    "Content Pillars",
                    value=profile.get("content_pillars") or ""
                )
                visual_guidelines = st.text_area(
                    "Visual Guidelines",
                    value=profile.get("visual_guidelines") or ""
                )
                brand_colors = st.text_input(
                    "Brand Colours",
                    value=profile.get("brand_colors") or ""
                )
                brand_fonts = st.text_input(
                    "Brand Fonts",
                    value=profile.get("brand_fonts") or ""
                )
                content_restrictions = st.text_area(
                    "Content Restrictions",
                    value=profile.get("content_restrictions") or ""
                )
                key_messages = st.text_area(
                    "Key Messages",
                    value=profile.get("key_messages") or ""
                )

                save_profile = st.form_submit_button(
                    "Save Brand Profile",
                    type="primary"
                )

                if save_profile:
                    update_brand_profile(
                        profile["id"],
                        {
                            "purpose": purpose,
                            "target_audience": target_audience,
                            "brand_values": brand_values,
                            "tone_of_voice": tone_of_voice,
                            "brand_personality": brand_personality,
                            "content_pillars": content_pillars,
                            "visual_guidelines": visual_guidelines,
                            "brand_colors": brand_colors,
                            "brand_fonts": brand_fonts,
                            "content_restrictions": content_restrictions,
                            "key_messages": key_messages
                        }
                    )

                    st.success("Brand profile saved successfully!")
                    st.rerun()

        else:
            st.info("Create a brand before editing its profile.")

    except Exception as error:
        st.error(f"Could not load brand profile: {error}")

    # ACCOUNT MANAGEMENT
    st.divider()
    st.markdown("### Invitations and Account Management")
    st.info("Invitations and account management will be added here.")


# MY DRAFTS LIBRARY
elif workflow == "My Drafts":

    st.subheader("My Drafts")
    st.write("Your saved content drafts.")

    if not selected_brand_id:
        st.warning("Please select a brand first.")

    else:

        saved_drafts = get_saved_content_drafts(
            selected_brand_id
        )

        if not saved_drafts:
            st.info(
                "You haven't saved any drafts for this brand yet."
            )

        else:

            workflow_filter = st.selectbox(
                "Filter by workflow",
                [
                    "All Workflows",
                    "Content Ideation",
                    "Editorial Review",
                    "Content Repurposing Studio"
                ],
                key="draft_workflow_filter"
            )

            filtered_drafts = saved_drafts

            if workflow_filter != "All Workflows":
                filtered_drafts = [
                    draft for draft in saved_drafts
                    if draft["workflow"] == workflow_filter
                ]

            st.caption(
                f"{len(filtered_drafts)} saved draft(s)"
            )

            for draft in filtered_drafts:

                with st.container(border=True):

                    st.markdown(f"**{draft['title']}**")

                    st.caption(
                        f"Workflow: {draft['workflow']}"
                    )

                    st.caption(
                        f"Last updated: {draft['updated_at']}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "Open Draft",
                            key=f"open_draft_{draft['id']}"
                        ):

                            draft_data = draft["draft_data"] 
                            saved_result = draft_data.get(
                                "generated_result",
                                {}
                            )

                            st.session_state.setdefault("brand_results", {})

                            if saved_result:
                                st.session_state["brand_results"][selected_brand_id] = saved_result
                            else:
                                st.session_state["brand_results"].pop(selected_brand_id, None)
                            draft_workflow = draft["workflow"]

                            save_content_draft(
                                selected_brand_id,
                                draft_workflow,
                                draft_data
                            )

                            if draft_workflow == "Content Ideation":

                                st.session_state[
                                    f"ideation_topic_{selected_brand_id}"
                                ] = draft_data.get("topic", "")

                                st.session_state[
                                    f"ideation_audience_{selected_brand_id}"
                                ] = draft_data.get("audience", "")

                                st.session_state[
                                    f"ideation_format_{selected_brand_id}"
                                ] = draft_data.get("format_type", "Reel")

                                st.session_state[
                                    f"ideation_tone_{selected_brand_id}"
                                ] = draft_data.get(
                                    "tone",
                                    "Engaging and relatable"
                                )

                            elif draft_workflow == "Editorial Review":

                                st.session_state[
                                    f"editorial_content_{selected_brand_id}"
                                ] = draft_data.get("content", "")

                            elif draft_workflow == "Content Repurposing Studio":

                                st.session_state[
                                    f"repurpose_source_{selected_brand_id}"
                                ] = draft_data.get(
                                    "source_option",
                                    "Paste text"
                                )

                                st.session_state[
                                    f"repurpose_text_{selected_brand_id}"
                                ] = draft_data.get("source_text", "")

                                st.session_state[
                                    f"repurpose_formats_{selected_brand_id}"
                                ] = draft_data.get("output_formats", [])

                            st.session_state["pending_workflow"] = (
                                draft_workflow
                            )

                            st.rerun()

                    with col2:

                        if st.button(
                            "Delete",
                            key=f"delete_draft_{draft['id']}"
                        ):

                            delete_saved_content_draft(
                                draft["id"]
                            )

                            st.success("Draft deleted.")
                            st.rerun()

# CONTENT IDEATION
elif workflow == "Content Ideation":

    st.subheader("Generate Content")

    if not selected_brand_id:
        st.warning("Please select a brand first.")

    else:
        draft_key = f"ideation_{selected_brand_id}"

        def clear_ideation_draft():
            delete_content_draft(
                selected_brand_id,
                "Content Ideation"
            )

            st.session_state[f"ideation_topic_{selected_brand_id}"] = ""
            st.session_state[f"ideation_audience_{selected_brand_id}"] = ""
            st.session_state[f"ideation_format_{selected_brand_id}"] = "Reel"
            st.session_state[f"ideation_tone_{selected_brand_id}"] = "Engaging and relatable"

        
        working_drafts = get_working_drafts(
            selected_brand_id,
            "Content Ideation"
        )

        if not working_drafts:
            old_draft = get_content_draft(
                selected_brand_id,
                "Content Ideation"
            ) or {}

            old_result = st.session_state.get(
                "brand_results", {}
            ).get(selected_brand_id, {})

            created = create_working_draft(
                selected_brand_id,
                "Content Ideation"
            )

            if created:
                new_draft = created[0]
                update_working_draft(
                    new_draft["id"],
                    old_draft,
                    old_result
                )
                st.session_state[f"active_ideation_{selected_brand_id}"] = new_draft["id"]
                st.rerun()

        working_drafts = get_working_drafts(
            selected_brand_id,
            "Content Ideation"
        )

        active_key = f"active_ideation_{selected_brand_id}"

        draft_options = {
            draft["id"]: draft["title"]
            for draft in working_drafts
        }

        if active_key not in st.session_state or st.session_state[active_key] not in draft_options:
            st.session_state[active_key] = working_drafts[0]["id"]

        selected_draft_id = st.selectbox(
            "Working Draft",
            options=list(draft_options.keys()),
            format_func=lambda draft_id: draft_options[draft_id],
            key=active_key
        )

        selected_working_draft = next(
            draft for draft in working_drafts
            if draft["id"] == selected_draft_id
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "＋ New Draft",
                key=f"new_working_ideation_{selected_brand_id}"
            ):
                created = create_working_draft(
                    selected_brand_id,
                    "Content Ideation"
                )

                if created:
                    new_draft = created[0]
                    st.session_state[active_key] = new_draft["id"]
                    st.session_state[f"ideation_topic_{selected_brand_id}"] = ""
                    st.session_state[f"ideation_audience_{selected_brand_id}"] = ""
                    st.session_state[f"ideation_format_{selected_brand_id}"] = "Reel"
                    st.session_state[f"ideation_tone_{selected_brand_id}"] = "Engaging and relatable"
                    st.session_state.setdefault("brand_results", {})
                    st.session_state["brand_results"].pop(selected_brand_id, None)
                    st.rerun()

        with col2:
            if st.button(
                "Delete Working Draft",
                key=f"delete_working_ideation_{selected_brand_id}"
            ):
                delete_working_draft(selected_draft_id)
                st.session_state.pop(active_key, None)
                st.rerun()

        saved_draft = selected_working_draft.get(
            "draft_data", {}
        ) or {}

                topic_key = f"ideation_topic_{selected_draft_id}"
        audience_key = f"ideation_audience_{selected_draft_id}"
        format_key = f"ideation_format_{selected_draft_id}"
        tone_key = f"ideation_tone_{selected_draft_id}"

        if topic_key not in st.session_state:
            st.session_state[topic_key] = saved_draft.get("topic", "")

        if audience_key not in st.session_state:
            st.session_state[audience_key] = saved_draft.get("audience", "")

        if format_key not in st.session_state:
            st.session_state[format_key] = saved_draft.get("format_type", "Reel")

        if tone_key not in st.session_state:
            st.session_state[tone_key] = saved_draft.get(
                "tone", "Engaging and relatable"
            )

        saved_result = selected_working_draft.get(
            "generated_result", {}
        ) or {}

        st.session_state.setdefault("brand_results", {})

        if saved_result:
            st.session_state["brand_results"][selected_brand_id] = saved_result
        else:
            st.session_state["brand_results"].pop(selected_brand_id, None)

        topic = st.text_input(
           "Content topic",
           key=topic_key
        )

        audience = st.text_input(
            "Target audience",
            key=audience_key
        )

        format_type = st.selectbox(
            "Content format",
            ["Reel", "Carousel"],
            key=format_key
        )

        tone = st.text_input(
            "Preferred tone",
            key=tone_key
        )

        current_draft = {
            "topic": topic,
            "audience": audience,
            "format_type": format_type,
            "tone": tone
        }

        has_content = (
            topic.strip()
            or audience.strip()
            or format_type != "Reel"
            or tone != "Engaging and relatable"
        )

        if current_draft != saved_draft:
            update_working_draft(
                selected_draft_id,
                current_draft,
                st.session_state.get("brand_results", {}).get(
                    selected_brand_id, {}
                )
            )

        st.caption("Your working draft is saved automatically.")


        draft_title = st.text_input(
            "Name this draft",
            key=f"saved_ideation_title_{selected_brand_id}",
            placeholder="e.g. December content ideas"
        )


        if st.button("Save Draft", key=f"save_ideation_{selected_brand_id}"):

            if not has_content:
                st.warning("Enter some content before saving.")

            elif not draft_title.strip():
                st.warning("Please give your draft a name.")

            else:
                try:
                    save_saved_content_draft(
                        selected_brand_id,
                        draft_title.strip(),
                        "Content Ideation",
                        {
                            **current_draft,
                            "generated_result": st.session_state.get(
                                "brand_results", {}
                            ).get(selected_brand_id, {})
                        }
                    )

                    st.success("Draft saved to My Drafts!")

                except Exception as error:
                    st.error(f"Could not save draft: {error}")
            

        st.button(
            "Clear Draft",
            on_click=clear_ideation_draft
        )

        if st.button("Generate Content", type="primary"):

            if not topic or not audience:
                st.warning(
                    "Please enter a topic and target audience."
                )

            else:
                with st.spinner("Generating content..."):

                    try:
                        result = generate_content_ideas(
                            topic,
                            audience,
                            format_type,
                            tone,
                            brand_name
                        )

                        st.session_state.setdefault("brand_results", {})
                        st.session_state["brand_results"][selected_brand_id] = {
                            "Content Ideas": result
                        }
                    except Exception as error:
                        st.error(
                            f"Generation failed: {error}"
                        )


# EDITORIAL REVIEW
elif workflow == "Editorial Review":

    st.subheader("Review Existing Content")

    if not selected_brand_id:
        st.warning("Please select a brand first.")

    else:

        def clear_editorial_draft():
            delete_content_draft(
                selected_brand_id,
                "Editorial Review"
            )
            st.session_state[
                f"editorial_content_{selected_brand_id}"
            ] = ""

        saved_draft = get_content_draft(
            selected_brand_id,
            "Editorial Review"
        )

        content = st.text_area(
            "Paste the content you want reviewed",
            value=saved_draft.get("content", ""),
            height=250,
            key=f"editorial_content_{selected_brand_id}"
        )

        current_draft = {"content": content}

        if content.strip() and current_draft != saved_draft:
            save_content_draft(
                selected_brand_id,
                "Editorial Review",
                current_draft
            )

        st.caption("Your draft is saved automatically.")

        draft_title = st.text_input(
            "Name this draft",
            key=f"saved_editorial_title_{selected_brand_id}",
            placeholder="e.g. November article review"
        )


        if st.button(
            "Save Draft",
            key=f"save_editorial_{selected_brand_id}"
        ):

            if not content.strip():
                st.warning("Enter some content before saving.")

            elif not draft_title.strip():
                st.warning("Please give your draft a name.")

            else:
                try:
                    save_saved_content_draft(
                        selected_brand_id,
                        draft_title.strip(),
                        "Editorial Review",
                        {
                            **current_draft,
                            "generated_result": st.session_state.get(
                                "brand_results", {}
                            ).get(selected_brand_id, {})
                        }
                    )

                    st.success("Draft saved to My Drafts!")

                except Exception as error:
                    st.error(f"Could not save draft: {error}")

        st.button(
            "Clear Draft",
            on_click=clear_editorial_draft
        )

        if st.button("Review Content", type="primary"):

            if not content.strip():
                st.warning("Please paste content first.")

            else:
                with st.spinner("Reviewing content..."):

                    try:
                        result = review_content(
                            content,
                            brand_name
                        )

                        st.session_state.setdefault("brand_results", {})
                        st.session_state["brand_results"][selected_brand_id] = {
                            "Editorial Review": result
                        }

                    except Exception as error:
                        st.error(
                            f"Review failed: {error}"
                        )


# CONTENT REPURPOSING STUDIO
elif workflow == "Content Repurposing Studio":

    st.subheader("Repurpose Existing Content")

    if not selected_brand_id:
        st.warning("Please select a brand first.")

    else:

        def clear_repurposing_draft():
            delete_content_draft(
                selected_brand_id,
                "Content Repurposing Studio"
            )

            st.session_state[
                f"repurpose_source_{selected_brand_id}"
            ] = "Paste text"

            st.session_state[
                f"repurpose_text_{selected_brand_id}"
            ] = ""

            st.session_state[
                f"repurpose_formats_{selected_brand_id}"
            ] = []

        saved_draft = get_content_draft(
            selected_brand_id,
            "Content Repurposing Studio"
        )

        source_option = st.radio(
            "Choose your source",
            [
                "Paste text",
                "Upload a document or image"
            ],
            index=(
                0 if saved_draft.get("source_option", "Paste text") == "Paste text"
                else 1
            ),
            key=f"repurpose_source_{selected_brand_id}"
        )

        source_text = None
        file_path = None
        uploaded_file = None

        if source_option == "Paste text":

            source_text = st.text_area(
                "Paste your source material",
                value=saved_draft.get("source_text", ""),
                height=250,
                key=f"repurpose_text_{selected_brand_id}"
            )

        else:

            st.info(
                "Uploaded files must be selected again after refreshing."
            )

            uploaded_file = st.file_uploader(
                "Upload PDF, DOCX or image",
                type=[
                    "pdf",
                    "docx",
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                key=f"repurpose_file_{selected_brand_id}"
            )

        output_options = [
            "Carousel",
            "Reel",
            "Blog Article",
            "Newsletter",
            "Social Media Caption"
        ]

        output_formats = st.multiselect(
            "Choose output formats",
            output_options,
            default=[
                item for item in saved_draft.get("output_formats", [])
                if item in output_options
            ],
            key=f"repurpose_formats_{selected_brand_id}"
        )

        current_draft = {
            "source_option": source_option,
            "source_text": source_text or "",
            "output_formats": output_formats
        }

        if current_draft != saved_draft:
            save_content_draft(
                selected_brand_id,
                "Content Repurposing Studio",
                current_draft
            )

        st.caption("Your text and output selections save automatically.")
        draft_title = st.text_input(
            "Name this draft",
            key=f"saved_repurposing_title_{selected_brand_id}",
            placeholder="e.g. December social campaign"
        )

        
        
        if st.button(
            "Save Draft",
            key=f"save_repurposing_{selected_brand_id}"
        ):

            has_text = bool((source_text or "").strip())
            has_file = uploaded_file is not None

            if not has_text and not has_file:
                st.warning(
                    "Paste source text or upload a file before saving."
                )

            elif not draft_title.strip():
                st.warning("Please give your draft a name.")

            elif not output_formats:
                st.warning("Please select at least one output format.")

            else:
                try:
                    save_data = {
                        "source_option": source_option,
                        "source_text": source_text,
                        "output_formats": output_formats,
                        "generated_result": st.session_state.get(
                            "brand_results", {}
                        ).get(selected_brand_id, {}),
                        "uploaded_file_name": (
                            uploaded_file.name if uploaded_file else None
                        )
                    }

                    save_saved_content_draft(
                        selected_brand_id,
                        draft_title.strip(),
                        "Content Repurposing Studio",
                        save_data
                    )

                    st.success("Draft saved to My Drafts!")

                except Exception as error:
                    st.error(f"Could not save draft: {error}")


        st.button(
            "Clear Draft",
            on_click=clear_repurposing_draft
        )

        if st.button("Repurpose Content", type="primary"):

            if (
                source_option == "Paste text"
                and not source_text.strip()
            ):
                st.warning(
                    "Please paste your source material."
                )

            elif (
                source_option == "Upload a document or image"
                and not uploaded_file
            ):
                st.warning("Please upload a file.")

            elif not output_formats:
                st.warning(
                    "Please select at least one output format."
                )

            else:
                try:

                    if uploaded_file:

                        suffix = os.path.splitext(
                            uploaded_file.name
                        )[1]

                        with tempfile.NamedTemporaryFile(
                            delete=False,
                            suffix=suffix
                        ) as temp_file:

                            temp_file.write(
                                uploaded_file.getvalue()
                            )

                            file_path = temp_file.name

                    with st.spinner(
                        "Processing and repurposing content..."
                    ):

                        result = run_contentflow_pipeline(
                            brand_name=brand_name,
                            output_formats=output_formats,
                            source_text=source_text,
                            file_path=file_path
                        )

                    st.session_state.setdefault("brand_results", {})
                    st.session_state["brand_results"][selected_brand_id] = {
                        "Content Repurposing Studio": result["generated_content"]
                    }

                except Exception as error:

                    st.error(
                        f"Repurposing failed: {error}"
                    )

                finally:

                    if file_path and os.path.exists(file_path):
                        os.remove(file_path)



# DISPLAY GENERATED CONTENT

current_result = st.session_state.get(
    "brand_results", {}
).get(selected_brand_id, {})

if current_result:

    st.divider()
    st.subheader("Your Content")

    for format_name, content in current_result.items():

        with st.expander(
            format_name,
            expanded=True
        ):
            st.write(content)

    if st.button("Prepare Word Document"):

        try:

            saved_files = save_generated_content(
                current_result,
                brand_name
            )

            for path in saved_files:

                with open(path, "rb") as document:

                    st.download_button(
                        label="Download Word Document",
                        data=document.read(),
                        file_name=os.path.basename(path),
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        )
                    )

        except Exception as error:

            st.error(
                f"Document export failed: {error}"
            )
