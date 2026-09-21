import streamlit as st
import pandas as pd
from pathlib import Path

# 1. Load the database safely using an absolute path
@st.cache_data
def load_data():
    # Resolve the exact folder where app.py lives
    current_dir = Path(__file__).parent
    csv_path = current_dir / "knowledge_db.csv"
    
    # Load using utf-8 (assuming you re-exported as CSV UTF-8) and semicolon separator
    try:
        df = pd.read_csv(csv_path, encoding="utf-8", sep=";")
    except FileNotFoundError:
        st.error(f"Could not find the database at {csv_path}. Please ensure 'knowledge_db.csv' exists.")
        st.stop()
        
    df.columns = df.columns.str.strip()
    return df

# 2. Initialize session state
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'user_choice' not in st.session_state:
    st.session_state.user_choice = None

df = load_data()

# Data Validation: Ensure required columns exist before proceeding
required_cols = ['Question', 'Choice A', 'Choice B', 'Choice C', 'Choice D', 'Correct Answer']
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Database is missing required columns: {missing_cols}")
    st.stop()

# App Header
st.title("Tech Support Mastery Quiz 🛠️")
st.markdown("Test your knowledge on pressure, temperature instrumentation, and troubleshooting!")

# 3. Game Logic
if st.session_state.current_index >= len(df):
    st.success(f"Quiz Complete! Your final score is {st.session_state.score}/{len(df)}")
    st.balloons()
    if st.button("Restart Quiz"):
        st.session_state.current_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.user_choice = None
        st.rerun()
else:
    row = df.iloc[st.session_state.current_index]

    # Display progress
    progress_val = st.session_state.current_index / len(df)
    st.progress(progress_val)
    st.write(f"**Score:** {st.session_state.score} | **Question:** {st.session_state.current_index + 1} of {len(df)}")
    st.write("---")

    # Display Question
    st.caption(f"Topic: {row.get('Topic', 'General')} | Difficulty: {row.get('Difficulty', 'N/A')} | Type: {row.get('Question Type', 'N/A')}")
    st.subheader(row['Question'])

    # Compile choices safely (ignores NaN values for True/False questions)
    choices = [str(row[col]) for col in ['Choice A', 'Choice B', 'Choice C', 'Choice D'] if pd.notna(row[col])]

    # Determine the correct answer text strictly based on the mapping
    correct_letter = str(row['Correct Answer']).strip().upper()
    choice_map = {'A': 'Choice A', 'B': 'Choice B', 'C': 'Choice C', 'D': 'Choice D'}
    
    if correct_letter not in choice_map:
        st.error(f"Database configuration error on Question {st.session_state.current_index + 1}: Invalid correct answer key '{correct_letter}'. Must be A, B, C, or D.")
        st.stop()
        
    correct_text = str(row[choice_map[correct_letter]])

    # UI for unanswered question
    if not st.session_state.answered:
        user_answer = st.radio("Select your answer:", choices, index=None)
        
        if st.button("Submit Answer"):
            if user_answer:
                st.session_state.user_choice = user_answer
                st.session_state.answered = True
                
                # BUG FIX: Score is only incremented exactly once upon submission
                if user_answer == correct_text:
                    st.session_state.score += 1
                    
                st.rerun()
            else:
                st.warning("Please select an answer before submitting.")
                
    # UI for answered question (Review Mode)
    else:
        st.radio("Your answer:", choices, index=choices.index(st.session_state.user_choice), disabled=True)
        
        if st.session_state.user_choice == correct_text:
            st.success("Correct! 🎉")
        else:
            st.error(f"Incorrect. The right answer was: **{correct_text}**")

        # Context Expander
        with st.expander("Behind the Answer (Learn More)", expanded=True):
            st.markdown(f"**🔬 Technical Reality:** {row.get('Technical Reality', 'N/A')}")
            st.markdown(f"**🌍 Real-World Analogy:** {row.get('Real-World Example / Analogy', 'N/A')}")
            st.markdown(f"**💬 Suggested Customer Response:** {row.get('Suggested Customer Response', 'N/A')}")
            st.markdown(f"**🔑 Key Takeaway:** {row.get('Key Takeaway', 'N/A')}")

        if st.button("Next Question"):
            st.session_state.current_index += 1
            st.session_state.answered = False
            st.session_state.user_choice = None
            st.rerun()