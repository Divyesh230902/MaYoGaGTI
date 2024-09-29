import streamlit as st
from models.llama_model import LlamaRoadmapManager
from services.database_service import update_user_profile, get_user_profile

def show_dashboard(roadmap_manager: LlamaRoadmapManager):
    st.title("MaYoGa GTI Learning Platform")

    username = st.session_state['username']
    user_profile = roadmap_manager.get_user_profile()

    st.subheader(f"Welcome, {username}!")
    st.write(f"**Role**: {user_profile['role']}")
    st.write(f"**Field of Study**: {user_profile['field_of_study']}")
    st.write(f"**Current Stage**: {user_profile['current_stage']}")
    st.write(f"**End Goal**: {user_profile['end_goal']}")

    if st.button("Edit Profile"):
        edit_profile(roadmap_manager)

    st.subheader("Your Learning Roadmap")
    roadmap = roadmap_manager.get_or_generate_roadmap(user_profile['end_goal'])

    if roadmap:
        display_roadmap_as_table(roadmap)

    if st.button("Regenerate Roadmap"):
        roadmap = roadmap_manager.generate_and_save_roadmap(user_profile['end_goal'])
        st.success("Roadmap regenerated successfully!")
        display_roadmap_as_table(roadmap)

def edit_profile(roadmap_manager: LlamaRoadmapManager):
    user_profile = roadmap_manager.get_user_profile()

    username = st.session_state['username']
    new_field_of_study = st.text_input("Field of Study", value=user_profile['field_of_study'])
    new_end_goal = st.text_input("End Goal", value=user_profile['end_goal'])

    if st.button("Update Profile"):
        update_user_profile(username, new_field_of_study, new_end_goal)
        st.success("Profile updated successfully!")
        st.experimental_rerun()

def display_roadmap_as_table(roadmap):
    # Iterate through the JSON roadmap and display it as a table
    st.write("Your Learning Roadmap in Table Format")
    for phase, milestones in roadmap.items():
        st.write(f"**{phase}**")
        for milestone, details in milestones.items():
            st.write(f"- **{milestone}**: {details}")