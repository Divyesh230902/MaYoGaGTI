import streamlit as st
from models.llama_model import LlamaRoadmapManager
from services.database_service import save_quiz_results, track_user_progress, get_user_progress

def show_analytics(roadmap_manager: LlamaRoadmapManager):
    st.title("Your Learning Analytics")

    username = st.session_state['username']
    progress_data = roadmap_manager.get_user_progress()

    # Display user streak and milestone progress
    st.subheader("Streak & Milestone Progress")
    st.write(f"Streak: {progress_data['streak']} days")

    # Display the current milestone and ask for quiz
    if progress_data['current_milestone']:
        current_phase, current_milestone = progress_data['current_milestone']
        st.subheader(f"Current Milestone: {current_phase} - {current_milestone}")
        
        if st.button("Take Quiz"):
            quiz = roadmap_manager.generate_quiz(current_phase, current_milestone)
            score = show_quiz(quiz)
            if score >= 80:
                st.success(f"Congratulations! You've completed the milestone with a score of {score}%")
                track_user_progress(username, current_phase, current_milestone)
            else:
                st.error(f"You scored {score}%. Let's review the knowledge gaps.")
                feedback = roadmap_manager.generate_gap_analysis(quiz)
                st.write(feedback)

def show_quiz(quiz):
    score = 0
    total_questions = len(quiz['questions'])

    for question_data in quiz['questions']:
        question = question_data['question']
        options = question_data['options']
        correct_answer = question_data['correct_answer']

        st.write(question)
        answer = st.radio("Choose an answer", options)

        if answer == correct_answer:
            score += 1

    return (score / total_questions) * 100