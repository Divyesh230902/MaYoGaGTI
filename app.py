import streamlit as st
from services.auth_service import login_user, register_user
from services.database_service import get_user_profile, update_user_profile, create_db
from models.llama_model import LlamaRoadmapManager
from streamlit_ui import analytics, dashboard  # Correct imports added for dashboard and analytics

def login_or_register():
    if 'username' not in st.session_state:
        st.session_state['username'] = None

    if st.session_state['username'] is None:
        st.title("Welcome to MaYoGa GTI Learning Platform")
        st.write("Please log in or register to access your personalized learning roadmap.")

        login_tab, register_tab = st.tabs(["Login", "Register"])

        # Login Tab
        with login_tab:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = login_user(username, password)
                if user:
                    st.session_state['username'] = username
                    st.experimental_rerun()  # Reload the page
                else:
                    st.error("Invalid username or password. Please try again.")

        # Register Tab
        with register_tab:
            st.subheader("Register")

            # Basic Registration Info
            username = st.text_input("Username", key="register_username")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
            role = st.radio("I am a...", ["Student", "Professional"], key="register_role")

            # Dynamic Questions based on Role
            if role == "Student":
                field_of_study = st.text_input("Field of Study")
                current_stage = st.selectbox("Current Stage of Study", ["Undergraduate", "Postgraduate", "PhD"])
            elif role == "Professional":
                job_title = st.text_input("Job Title")
                industry = st.text_input("Industry")
                years_of_experience = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)

            end_goal = st.text_input("What is your end goal? (e.g., AI Scientist, Data Analyst, etc.)")

            # Register Button
            if st.button("Register"):
                if password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    if role == "Student":
                        current_stage_info = current_stage
                        field_info = field_of_study
                    else:
                        current_stage_info = f"Job Title: {job_title}, Industry: {industry}, Years of Experience: {years_of_experience}"
                        field_info = industry

                    register_user(username, password, role, current_stage_info, field_info, end_goal)
                    st.success("Registration successful! Please log in.")
                    st.session_state['username'] = username
                    st.experimental_rerun()

    else:
        st.write(f"Welcome, {st.session_state['username']}!")
        st.button("Logout", on_click=lambda: st.session_state.update({'username': None}))

def main():
    # Show sidebar only if the user is logged in
    if st.session_state.get('username'):
        create_sidebar()

    if 'username' not in st.session_state or st.session_state['username'] is None:
        login_or_register()
    else:
        roadmap_manager = LlamaRoadmapManager(st.session_state['username'])

        if st.session_state.get('selected_page') == 'Dashboard':
            dashboard.show_dashboard(roadmap_manager)  # Corrected dashboard function call
        elif st.session_state.get('selected_page') == 'Analytics':
            analytics.show_analytics(roadmap_manager)  # Corrected analytics function call

def create_sidebar():
    st.sidebar.title(f"Welcome, {st.session_state.get('username', 'Guest')}!")

    st.sidebar.radio("Navigate", ['Dashboard', 'Analytics', 'Logout'], key='selected_page')

    if st.sidebar.button("Logout"):
        st.session_state['username'] = None
        st.experimental_rerun()

if __name__ == "__main__":
    create_db()
    main()