"""
app.py — brew-match Streamlit app

Quiz flow:
  1. Welcome page  →  Start Quiz button
  2. Quiz page     →  One question at a time, Back/Next, progress bar
  3. Results page  →  Plain-English fingerprint, radar chart + legend,
                      full buying guidance with context-specific country/process
                      descriptions, compact runner-up, shareable card
"""

import streamlit as st
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(__file__))
from matching import (
    find_match, QUESTIONS, GLOSSARY,
    COUNTRY_PROFILES, PROCESS_PROFILES, VARIETY_PROFILES
)

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="brew-match",
    page_icon="☕",
    layout="centered",
)

# ---------------------------------------------------------------------------
# STYLES
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .stApp { background-color: #1C1410; color: #F5ECD7; font-family: 'Georgia', serif; }
    .block-container { max-width: 680px; padding-top: 3rem; padding-bottom: 3rem; }
    header, footer { visibility: hidden; }
    .stProgress > div > div { background-color: #C8813A; }
    .stRadio label { color: #F5ECD7 !important; font-size: 1rem; }
    .stButton > button {
        background-color: #C8813A; color: #1C1410; border: none;
        border-radius: 4px; font-weight: bold; padding: 0.5rem 1.5rem;
    }
    .stButton > button:hover { background-color: #E09A50; color: #1C1410; }
    .result-card {
        background-color: #2A1F16; border-left: 4px solid #C8813A;
        border-radius: 6px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
    }
    .result-label {
        color: #C8813A; font-size: 0.72rem; text-transform: uppercase;
        letter-spacing: 0.1em; margin-bottom: 0.4rem;
    }
    .glossary-note { color: #9A8070; font-size: 0.82rem; font-style: italic; margin-top: 0.5rem; }
    .profile-item { color: #C8A882; font-size: 0.85rem; margin-top: 0.25rem; }
    .confidence-badge {
        display: inline-block; background-color: #3A2A1A; border: 1px solid #C8813A;
        color: #C8813A; border-radius: 20px; padding: 0.2rem 0.8rem;
        font-size: 0.8rem; margin-bottom: 1rem;
    }
    .runner-up-card {
        background-color: #1F1810; border: 1px solid #4A3828;
        border-radius: 6px; padding: 1.4rem 1.5rem; margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .fingerprint-box {
        background-color: #2A1F16; border-radius: 6px;
        padding: 1rem 1.5rem; margin-bottom: 1.5rem;
    }
    .context-name {
        color: #F5ECD7; font-weight: bold; font-size: 0.95rem;
        margin-top: 0.8rem; margin-bottom: 0.2rem;
    }
    .context-desc {
        color: #C8A882; font-size: 0.83rem; line-height: 1.5;
        padding-left: 0.8rem; border-left: 2px solid #3A2A1A;
    }
    .legend-table {
        width: 100%; border-collapse: collapse; font-size: 0.82rem;
        margin-top: 0.5rem; margin-bottom: 1.5rem;
    }
    .legend-table td { padding: 0.3rem 0.5rem; color: #C8A882; }
    .legend-table td:nth-child(1) { color: #F5ECD7; font-weight: bold; width: 30%; }
    .legend-table td:nth-child(2) { text-align: center; color: #9A8070; width: 35%; }
    .legend-table td:nth-child(3) { text-align: right; width: 35%; }
    .legend-table tr { border-bottom: 1px solid #2A1F16; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------

if "page"     not in st.session_state: st.session_state.page     = "welcome"
if "question" not in st.session_state: st.session_state.question = 0
if "answers"  not in st.session_state: st.session_state.answers  = [None] * 10

def go_to(page):
    st.session_state.page = page
    st.rerun()

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def axis_to_english(axis, score):
    """Converts a numeric axis score to a plain English preference description."""
    descriptions = {
        "roast": {
            (-2.0, -1.5): "Light roast (delicate, tea-like)",
            (-1.5, -0.5): "Light to light-medium roast",
            (-0.5,  0.5): "Medium roast (balanced)",
            ( 0.5,  1.5): "Medium-dark roast",
            ( 1.5,  2.0): "Dark roast (bold, intense)",
        },
        "acidity": {
            (-2.0, -1.5): "Very smooth (prefers no tartness)",
            (-1.5, -0.5): "Low acidity (mild, soft)",
            (-0.5,  0.5): "Moderate acidity",
            ( 0.5,  1.5): "Enjoys brightness and tang",
            ( 1.5,  2.0): "Loves acidity — the brighter the better",
        },
        "flavor": {
            (-2.0, -1.5): "Chocolatey and nutty",
            (-1.5, -0.5): "Caramel and spice leaning",
            (-0.5,  0.5): "Neutral / caramel-vanilla",
            ( 0.5,  1.5): "Mild fruit and citrus",
            ( 1.5,  2.0): "Bold fruity and floral",
        },
        "body": {
            (-2.0, -1.5): "Light body (tea-like, delicate)",
            (-1.5, -0.5): "Light to medium body",
            (-0.5,  0.5): "Medium body",
            ( 0.5,  1.5): "Medium to full body",
            ( 1.5,  2.0): "Full body (syrupy, heavy)",
        },
        "adventurousness": {
            (-2.0, -1.5): "Prefers familiar and classic",
            (-1.5, -0.5): "Mostly sticks to safe choices",
            (-0.5,  0.5): "Occasionally open to something new",
            ( 0.5,  1.5): "Pretty open to unusual coffees",
            ( 1.5,  2.0): "Actively seeks funky and experimental",
        },
    }
    for (low, high), label in descriptions[axis].items():
        if low <= score <= high:
            return label
    return str(score)


def render_fingerprint(axis_scores):
    """Plain-English translation of each axis score."""
    axis_labels = {
        "roast":           "☕  Roast preference",
        "acidity":         "⚡  Acidity tolerance",
        "flavor":          "🍓  Flavor family",
        "body":            "💧  Body preference",
        "adventurousness": "🌟  Adventurousness",
    }
    html = '<div class="fingerprint-box">'
    for axis, label in axis_labels.items():
        english = axis_to_english(axis, axis_scores[axis])
        html += f'<div class="profile-item"><strong>{label}:</strong> {english}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_radar_chart(axis_scores):
    """
    Radar chart with simple axis names (no directional labels — those
    are handled by the legend table below the chart instead).
    """
    axes   = ["Roast", "Acidity", "Flavor", "Body", "Adventurousness"]
    scores = [
        axis_scores["roast"],
        axis_scores["acidity"],
        axis_scores["flavor"],
        axis_scores["body"],
        axis_scores["adventurousness"],
    ]
    display        = [s + 2 for s in scores]  # shift -2→+2 to 0→4 for Plotly
    display_closed = display + [display[0]]
    axes_closed    = axes   + [axes[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=display_closed,
        theta=axes_closed,
        fill="toself",
        fillcolor="rgba(200, 129, 58, 0.25)",
        line=dict(color="#C8813A", width=2),
        marker=dict(color="#C8813A", size=6),
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1C1410",
            radialaxis=dict(
                visible=True,
                range=[0, 4],
                tickvals=[0, 1, 2, 3, 4],
                ticktext=["Min", "", "Mid", "", "Max"],
                tickfont=dict(color="#9A8070", size=9),
                gridcolor="#3A2A1A",
                linecolor="#3A2A1A",
            ),
            angularaxis=dict(
                tickfont=dict(color="#F5ECD7", size=11),
                gridcolor="#3A2A1A",
                linecolor="#3A2A1A",
            ),
        ),
        paper_bgcolor="#1C1410",
        plot_bgcolor="#1C1410",
        showlegend=False,
        margin=dict(t=40, b=40, l=60, r=60),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_radar_legend():
    """
    A simple table below the radar chart showing what low and high
    means for each axis — cleaner than cramming labels into the chart.
    """
    st.markdown("""
    <table class="legend-table">
        <tr>
            <td>Roast</td>
            <td>← Low = Light roast</td>
            <td>High = Dark roast →</td>
        </tr>
        <tr>
            <td>Acidity</td>
            <td>← Low = Smooth</td>
            <td>High = Bright & tangy →</td>
        </tr>
        <tr>
            <td>Flavor</td>
            <td>← Low = Chocolate/nutty</td>
            <td>High = Fruity/floral →</td>
        </tr>
        <tr>
            <td>Body</td>
            <td>← Low = Light, tea-like</td>
            <td>High = Heavy, syrupy →</td>
        </tr>
        <tr>
            <td>Adventurousness</td>
            <td>← Low = Classic</td>
            <td>High = Funky & experimental →</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)


def render_guidance_cards(guidance, show_context=True):
    """
    Renders buying guidance cards. Each country and process gets its own
    st.markdown() call (not one big HTML block) to avoid Streamlit rendering bugs.
    """

    def card(label, value, glossary_key=None):
        if isinstance(value, list):
            value_str = ", ".join(value)
        else:
            value_str = value
        gloss_html = ""
        if glossary_key and glossary_key in GLOSSARY:
            gloss_html = f'<div class="glossary-note">{GLOSSARY[glossary_key]}</div>'
        st.markdown(f"""
        <div class="result-card">
            <div class="result-label">{label}</div>
            <div>{value_str}</div>
            {gloss_html}
        </div>
        """, unsafe_allow_html=True)

    # Countries card
    card("Countries", guidance["countries"])

    # Per-country context — one st.markdown call per country (avoids rendering bug)
    if show_context:
        for country in guidance["countries"]:
            if country in COUNTRY_PROFILES:
                st.markdown(
                    f'<div class="context-name">{country}</div>'
                    f'<div class="context-desc">{COUNTRY_PROFILES[country]}</div>',
                    unsafe_allow_html=True
                )
        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    card("Regions",   guidance["regions"],   "regions")

    # Process card
    card("Process", guidance["process"])

    # Per-process context — one st.markdown call per process
    if show_context:
        for process in guidance["process"]:
            if process in PROCESS_PROFILES:
                st.markdown(
                    f'<div class="context-name">{process}</div>'
                    f'<div class="context-desc">{PROCESS_PROFILES[process]}</div>',
                    unsafe_allow_html=True
                )
        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    # Varieties card
    card("Varieties", guidance["varieties"], "varieties")

    # Per-variety context — one st.markdown call per variety
    if show_context:
        for variety in guidance["varieties"]:
            if variety in VARIETY_PROFILES:
                st.markdown(
                    f'<div class="context-name">{variety}</div>'
                    f'<div class="context-desc">{VARIETY_PROFILES[variety]}</div>',
                    unsafe_allow_html=True
                )
        st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

    card("Roast level",                   guidance["roast_level"],  "roast_level")
    card("Flavor notes to look for",      guidance["flavor_notes"], "flavor_notes")
    card("Roasters known for this style", guidance["roasters"],     "roasters")


def render_runner_up(runner_up):
    """
    Compact runner-up section — name, one-line description, and a single
    summary sentence of what to look for. No full guidance cards.
    """
    ru = runner_up
    g  = ru["guidance"]

    top_notes    = ", ".join(g["flavor_notes"][:3])
    countries    = ", ".join(g["countries"][:2])
    roasters     = ", ".join(g["roasters"][:2])
    process      = ", ".join(g["process"][:2])
    roast        = g["roast_level"]

    summary = (
        f"Look for <strong>{process}</strong> coffees from <strong>{countries}</strong>, "
        f"<strong>{roast}</strong> roast, with notes of <strong>{top_notes}</strong>. "
        f"Try: <strong>{roasters}</strong>."
    )

    st.markdown(f"""
    <div class="runner-up-card">
        <div class="result-label">Your runner-up archetype</div>
        <div style="font-size: 1.05rem; font-weight: bold; margin-bottom: 0.4rem;">
            {ru['name']}
        </div>
        <div style="color: #C8A882; font-size: 0.9rem; margin-bottom: 0.8rem;">
            {ru['description']}
        </div>
        <div style="color: #F5ECD7; font-size: 0.85rem; line-height: 1.6;">
            {summary}
        </div>
    </div>
    """, unsafe_allow_html=True)


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
        st.session_state.answers  = [None] * 10
        st.session_state.question = 0
        go_to("quiz")


# ---------------------------------------------------------------------------
# PAGE 2: QUIZ
# ---------------------------------------------------------------------------

def show_quiz():
    q_index = st.session_state.question
    q       = QUESTIONS[q_index]

    st.progress(q_index / len(QUESTIONS))
    st.caption(f"Question {q_index + 1} of {len(QUESTIONS)}")
    st.markdown(f"### {q['text']}")
    st.markdown("")

    option_labels  = [o[0] for o in q["options"]]
    current_answer = st.session_state.answers[q_index]
    current_scores = [o[1] for o in q["options"]]
    default_index  = current_scores.index(current_answer) if current_answer in current_scores else None

    selected_label = st.radio("", option_labels, index=default_index, key=f"q_{q_index}")

    st.markdown("")
    col1, col2 = st.columns([1, 1])

    selected_score = None
    if selected_label:
        for label, score in q["options"]:
            if label == selected_label:
                selected_score = score
                break
    if selected_score is not None:
        st.session_state.answers[q_index] = selected_score

    with col1:
        if q_index > 0:
            if st.button("← Back"):
                st.session_state.question -= 1
                st.rerun()

    with col2:
        if q_index == len(QUESTIONS) - 1:
            if st.button("See my results →", disabled=selected_score is None):
                go_to("results")
        else:
            if st.button("Next →", disabled=selected_score is None):
                st.session_state.question += 1
                st.rerun()


# ---------------------------------------------------------------------------
# PAGE 3: RESULTS
# ---------------------------------------------------------------------------

def show_results():
    result = find_match(st.session_state.answers)
    g      = result["guidance"]

    # Archetype name + confidence
    st.markdown(f"## ☕ You're a **{result['name']}**")
    st.markdown(
        f'<div class="confidence-badge">{result["confidence"]}</div>',
        unsafe_allow_html=True
    )
    st.markdown(result["description"])

    # Plain-English fingerprint
    st.markdown("### Your taste profile")
    st.caption("Here's what your answers say about your preferences — in plain English.")
    render_fingerprint(result["axis_scores"])

    # Radar chart + legend table
    st.caption("The shape below shows the same profile visually.")
    render_radar_chart(result["axis_scores"])
    render_radar_legend()

    # Full buying guidance
    st.markdown("### What to look for when buying")
    render_guidance_cards(g, show_context=True)

    # Compact runner-up
    st.markdown("### Also worth exploring")
    render_runner_up(result["runner_up"])

    # Shareable card
    st.markdown("### Share your result")
    share_text = (
        f"☕ brew-match result: {result['name']}\n"
        f"{result['description']}\n\n"
        f"Top flavor notes: {', '.join(g['flavor_notes'][:3])}\n"
        f"Try it at: https://brew-match.streamlit.app/"
    )
    st.code(share_text, language=None)
    st.caption("Copy and paste into Reddit, a group chat, or wherever you share things.")

    st.markdown("---")
    if st.button("← Retake quiz"):
        st.session_state.answers  = [None] * 10
        st.session_state.question = 0
        go_to("welcome")


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------

if st.session_state.page == "welcome":
    show_welcome()
elif st.session_state.page == "quiz":
    show_quiz()
elif st.session_state.page == "results":
    show_results()
