import streamlit as st
from services.auth_service import login_user, register_user
from models.llama_model import LlamaRoadmapManager
from services.database_service import get_user_profile, create_db
from streamlit_ui import analytics, dashboard

# Initialize the database
create_db()

# Main app function
def main():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Handle login and registration
    if not st.session_state["authenticated"]:
        login_or_register()
    else:
        # Fetch the user's profile after login
        user_profile = get_user_profile(st.session_state['username'])

        # Check if user profile exists
        if not user_profile:
            st.error("User profile not found. Please make sure you are registered.")
            return

        # Initialize LlamaRoadmapManager with user profile data
        roadmap_manager = LlamaRoadmapManager(
            username=user_profile['username'],
            role=user_profile['role'],
            current_stage=user_profile['current_stage'],
            field_of_study=user_profile['field_of_study'],
            end_goal=user_profile['end_goal']
        )

        # Sidebar for navigation
        st.sidebar.title(f"Welcome, {st.session_state['username']}!")
        page = st.sidebar.radio("Navigate", ["Dashboard", "Analytics", "Logout"])

        if page == "Dashboard":
            dashboard.show_dashboard(roadmap_manager)
        elif page == "Analytics":
            analytics.show_analytics(roadmap_manager)
        elif page == "Logout":
            st.session_state["authenticated"] = False
            st.experimental_rerun()

# Login or Registration page
def login_or_register():
    st.title("Login / Register")

    option = st.radio("Choose an option:", ["Login", "Register"])

    if option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.experimental_rerun()
            else:
                st.error("Invalid login details")
    
    elif option == "Register":
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        role = st.radio("Select your role", ["Student", "Professional"])
        current_stage = st.text_input(f"Enter your {role} stage")
        field_of_study = st.text_input("Field of study or job role")
        end_goal = st.text_input("What is your end goal?")

        if st.button("Register"):
            if password == confirm_password:
                register_user(username, password, role, current_stage, field_of_study, end_goal)
                st.success("User registered successfully! Please login.")
            else:
                st.error("Passwords do not match. Please try again.")

# Run the main function
if __name__ == "__main__":
    main()