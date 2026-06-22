"""
app.py — brew-match Streamlit app

Quiz flow:
  1. Welcome page  →  Start Quiz button
  2. Quiz page     →  One question at a time, Back/Next buttons, progress bar
  3. Results page  →  Archetype name, description, and full buying guidance

How session state works (new concept):
  Normally, every time a user clicks a button in Streamlit, the entire script
  re-runs from top to bottom — like refreshing the page. This means any
  variables you set (like "which question are we on?") get wiped out.

  st.session_state is a special dictionary that PERSISTS across those reruns.
  Think of it as Streamlit's memory for a single user's session.

  We store three things in session state:
    - page:     which screen we're on ("welcome", "quiz", "results")
    - question: which question the user is currently on (0–9)
    - answers:  a list of 10 scores, filled in as the user answers
"""

import streamlit as st
import sys
import os

# Make sure Python can find matching.py (it's in the same folder as this file)
sys.path.append(os.path.dirname(__file__))
from matching import find_match, QUESTIONS

# ---------------------------------------------------------------------------
# PAGE CONFIG — must be the first Streamlit call in the file
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="brew-match",
    page_icon="☕",
    layout="centered",
)

# ---------------------------------------------------------------------------
# CUSTOM STYLES
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    /* Overall background and font */
    .stApp {
        background-color: #1C1410;
        color: #F5ECD7;
        font-family: 'Georgia', serif;
    }

    /* Main content area */
    .block-container {
        max-width: 680px;
        padding-top: 3rem;
        padding-bottom: 3rem;
    }

    /* Hide default Streamlit header/footer */
    header, footer { visibility: hidden; }

    /* Progress bar color */
    .stProgress > div > div {
        background-color: #C8813A;
    }

    /* Radio button labels */
    .stRadio label {
        color: #F5ECD7 !important;
        font-size: 1rem;
    }

    /* Buttons */
    .stButton > button {
        background-color: #C8813A;
        color: #1C1410;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover {
        background-color: #E09A50;
        color: #1C1410;
    }

    /* Result card */
    .result-card {
        background-color: #2A1F16;
        border-left: 4px solid #C8813A;
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }

    /* Section label inside result card */
    .result-label {
        color: #C8813A;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE INITIALIZATION
# Run once at the start of each session — sets defaults if keys don't exist yet
# ---------------------------------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "question" not in st.session_state:
    st.session_state.question = 0

if "answers" not in st.session_state:
    # None means unanswered; gets replaced with a score (-2 to +2) as user answers
    st.session_state.answers = [None] * 10

# ---------------------------------------------------------------------------
# HELPER: go to a different page
# ---------------------------------------------------------------------------

def go_to(page):
    st.session_state.page = page
    st.rerun()  # immediately re-run the script so the new page renders

# ---------------------------------------------------------------------------
# PAGE 1: WELCOME
# ---------------------------------------------------------------------------

def show_welcome():
    st.markdown("## ☕ brew-match")
    st.markdown("#### Find your perfect cup")
    st.markdown("""
    Not sure what coffee to buy next? Answer 10 quick questions about
    your taste preferences and we'll match you to your coffee archetype —
    plus tell you exactly what to look for when shopping.
    """)
    st.markdown("---")
    st.markdown("**Takes about 2 minutes. No coffee knowledge required.**")

    if st.button("Start Quiz →"):
        # Reset answers in case user is retaking the quiz
        st.session_state.answers = [None] * 10
        st.session_state.question = 0
        go_to("quiz")

# ---------------------------------------------------------------------------
# PAGE 2: QUIZ (one question at a time)
# ---------------------------------------------------------------------------

def show_quiz():
    q_index = st.session_state.question
    q = QUESTIONS[q_index]

    # Progress bar — shows how far through the quiz the user is
    progress = q_index / len(QUESTIONS)
    st.progress(progress)
    st.caption(f"Question {q_index + 1} of {len(QUESTIONS)}")

    # Question text
    st.markdown(f"### {q['text']}")
    st.markdown("")

    # Build the list of display labels for the radio buttons
    # Each option is a tuple: (display_label, score)
    option_labels = [option[0] for option in q["options"]]

    # Figure out which option is currently selected (if any)
    # so the radio button remembers the user's previous selection
    current_answer = st.session_state.answers[q_index]
    current_scores = [option[1] for option in q["options"]]

    if current_answer is not None and current_answer in current_scores:
        default_index = current_scores.index(current_answer)
    else:
        default_index = None  # nothing selected yet

    # Render the radio buttons — user picks one of 5 options
    selected_label = st.radio(
        label="",           # question text is already shown above
        options=option_labels,
        index=default_index,
        key=f"q_{q_index}",  # unique key per question so Streamlit tracks them separately
    )

    st.markdown("")

    # Back / Next buttons side by side
    col1, col2 = st.columns([1, 1])

    with col1:
        if q_index > 0:
            if st.button("← Back"):
                st.session_state.question -= 1
                st.rerun()

    with col2:
        # Work out the score for whichever option is selected
        selected_score = None
        if selected_label is not None:
            for label, score in q["options"]:
                if label == selected_label:
                    selected_score = score
                    break

        # Save the answer to session state as soon as something is selected
        if selected_score is not None:
            st.session_state.answers[q_index] = selected_score

        # Last question: show "See my results" instead of "Next"
        if q_index == len(QUESTIONS) - 1:
            results_ready = selected_score is not None
            if st.button("See my results →", disabled=not results_ready):
                go_to("results")
        else:
            if st.button("Next →", disabled=selected_score is None):
                st.session_state.question += 1
                st.rerun()

# ---------------------------------------------------------------------------
# PAGE 3: RESULTS
# ---------------------------------------------------------------------------

def show_results():
    # Run the matching logic against the user's 10 answers
    result = find_match(st.session_state.answers)
    g = result["guidance"]

    # Archetype name and description
    st.markdown(f"## ☕ You're a **{result['name']}**")
    st.markdown(result["description"])
    st.markdown("---")
    st.markdown("### What to look for when buying")

    # Each guidance field in its own card
    def card(label, value):
        if isinstance(value, list):
            value = ", ".join(value)
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">{label}</div>
            <div>{value}</div>
        </div>
        """, unsafe_allow_html=True)

    card("Countries", g["countries"])
    card("Regions", g["regions"])
    card("Process", g["process"])
    card("Varieties", g["varieties"])
    card("Roast level", g["roast_level"])
    card("Flavor notes to look for", g["flavor_notes"])
    card("Roasters known for this style", g["roasters"])

    st.markdown("---")

    # Retake button
    if st.button("← Retake quiz"):
        st.session_state.answers = [None] * 10
        st.session_state.question = 0
        go_to("welcome")

# ---------------------------------------------------------------------------
# ROUTER — decides which page to show based on session state
# ---------------------------------------------------------------------------

if st.session_state.page == "welcome":
    show_welcome()
elif st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "results":
    show_results()
