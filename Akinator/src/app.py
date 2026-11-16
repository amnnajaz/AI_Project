
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from knowledge_base import KnowledgeBase
from game_agent import GameAgent
from question_selector import InfoGainSelector, RandomSelector


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "knowledge_base.csv"

MAX_QUESTIONS = 20
CONFIDENCE_THRESHOLD = 0.85

ANSWER_OPTIONS = {
    "Yes": "yes",
    "Probably": "probably",
    "Don't know": "dont_know",
    "Probably not": "probably_not",
    "No": "no"
}

st.set_page_config(
    page_title="Guess Who I Am?",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f1f2f6;
    }

    .hero {
        background: linear-gradient(120deg, #292b69, #6257b8);
        padding: 32px;
        border-radius: 18px;
        margin-bottom: 25px;
    }

    .hero-title {
        color: white;
        font-size: 38px;
        font-weight: 750;
    }

    .hero-description {
        color: #eeeeff;
        font-size: 16px;
        margin-top: 8px;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7ef;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label p {
        color: #555b75 !important;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #292b69 !important;
    }

    .stProgress > div > div > div > div {
        background-color: #7165c5;
    }

    div.stButton > button {
        border-radius: 9px;
        min-height: 42px;
        font-weight: 600;
    }

    [data-testid="stSidebar"] {
        background-color: #171b26;
    }

    .question-label {
        color: #7165c5;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .question-card {
        background-color: #ffffff;
        padding: 28px;
        border-radius: 15px;
        margin: 15px 0;
    }

    .question-card h2 {
        color: #292b69 !important;
        text-align: center;
        font-size: 25px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOAD KNOWLEDGE BASE
# --------------------------------------------------

@st.cache_resource
def load_knowledge_base():
    return KnowledgeBase.from_csv(DATA_PATH)


try:
    kb = load_knowledge_base()
except Exception as error:
    st.error(f"Could not load the knowledge base: {error}")
    st.stop()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

def initialize_state():

    defaults = {
        "agent": None,
        "game_started": False,
        "game_over": False,
        "awaiting_confirmation": False,
        "confirmed_correct": None,
        "strategy": "Information Gain",
        "candidate_added": False,
        "added_candidate_name": None,
        "add_candidate_error": None
    }

    for key, value in defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# --------------------------------------------------
# GAME FUNCTIONS
# --------------------------------------------------

def start_game(strategy_name):

    if strategy_name == "Information Gain":
        selector = InfoGainSelector()
    else:
        selector = RandomSelector(seed=42)

    st.session_state.agent = GameAgent(
        kb=kb,
        selector=selector,
        max_questions=MAX_QUESTIONS,
        confidence_threshold=CONFIDENCE_THRESHOLD
    )

    st.session_state.game_started = True
    st.session_state.game_over = False
    st.session_state.awaiting_confirmation = False
    st.session_state.confirmed_correct = None
    st.session_state.strategy = strategy_name

    st.session_state.candidate_added = False
    st.session_state.added_candidate_name = None
    st.session_state.add_candidate_error = None


def reset_game():

    st.session_state.agent = None
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.awaiting_confirmation = False
    st.session_state.confirmed_correct = None

    st.session_state.candidate_added = False
    st.session_state.added_candidate_name = None
    st.session_state.add_candidate_error = None


# --------------------------------------------------
# ADD MISSING CANDIDATE
# --------------------------------------------------

def add_missing_candidate(name):

    name = name.strip()

    if not name:
        st.session_state.add_candidate_error = (
            "Please enter the correct candidate's name."
        )
        return

    existing_names = {
        candidate.casefold() for candidate in kb.names
    }

    if name.casefold() in existing_names:
        st.session_state.add_candidate_error = (
            "This candidate already exists in the knowledge base."
        )
        return

    agent = st.session_state.agent

    answers = {
        kb.attributes[attribute_index]: answer
        for attribute_index, answer in zip(
            agent.belief.asked,
            agent.belief.answers
        )
    }

    try:

        kb.add_candidate(name, answers)

        try:
            kb.save_csv(DATA_PATH)

        except Exception:
            kb.names.pop()
            kb.matrix = kb.matrix[:-1]
            raise

        st.session_state.candidate_added = True
        st.session_state.added_candidate_name = name
        st.session_state.add_candidate_error = None

    except Exception as error:

        st.session_state.add_candidate_error = (
            f"Could not add candidate: {error}"
        )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🎭 Game Settings")

    st.write("Choose the question selection strategy.")

    strategy_choice = st.selectbox(
        "Selection Strategy",
        ["Information Gain", "Random"],
        key="strategy_choice"
    )

    if st.session_state.game_started:

        st.caption(
            f"Active strategy: {st.session_state.strategy}"
        )

        if strategy_choice != st.session_state.strategy:

            if st.button(
                "Apply Strategy & Restart",
                type="primary",
                use_container_width=True
            ):
                start_game(strategy_choice)
                st.rerun()

    st.divider()

    st.subheader("How to Play")

    st.write("""
    1. Think of a Pakistani personality or place.
    2. Keep your choice secret.
    3. Answer the AI's questions.
    4. Watch its predictions change.
    5. See whether it can guess correctly!
    """)

    st.divider()

    st.caption("AL-2002 Artificial Intelligence Project")
    st.caption("Guess Who I Am?")


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-title">🎭 Guess Who I Am?</div>
    <div class="hero-description">
        Think of a Pakistani personality or place.
        I'll ask questions and try to figure out your choice!
    </div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# WELCOME SCREEN
# --------------------------------------------------

if not st.session_state.game_started:

    st.subheader("Ready to Play?")

    st.write(
        "Choose a Pakistani personality or place and keep it in mind. "
        "Don't reveal your choice!"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Candidates", len(kb))

    with col2:
        st.metric("Maximum Questions", MAX_QUESTIONS)

    with col3:
        st.metric("Confidence Threshold", "85%")

    st.info(
        "Answer using Yes, Probably, Don't know, "
        "Probably not, or No."
    )

    if st.button(
        "🚀 Start Game",
        type="primary",
        use_container_width=True
    ):
        start_game(strategy_choice)
        st.rerun()


# --------------------------------------------------
# ACTIVE GAME
# --------------------------------------------------

else:

    agent = st.session_state.agent

    question_count = len(agent.belief.asked)

    # --------------------------------------------------
    # GAME PROGRESS
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Questions Asked",
            f"{question_count}/{MAX_QUESTIONS}"
        )

    with col2:
        st.metric(
            "Current Strategy",
            st.session_state.strategy
        )

    st.progress(min(question_count / MAX_QUESTIONS, 1.0))

    st.divider()

    # --------------------------------------------------
    # LIVE PREDICTIONS
    # --------------------------------------------------

    st.subheader("🔍 My Current Predictions")

    predictions = agent.belief.top_k(3)

    prediction_columns = st.columns(3)

    for i, (name, probability) in enumerate(predictions):

        with prediction_columns[i]:

            with st.container(border=True):

                st.caption(f"PREDICTION #{i + 1}")

                st.markdown(f"**{name}**")

                st.progress(
                    min(max(float(probability), 0.0), 1.0)
                )

                st.caption(
                    f"Confidence: {probability * 100:.2f}%"
                )

    st.divider()

    # --------------------------------------------------
    # ASK QUESTION
    # --------------------------------------------------

    if (
        not st.session_state.game_over
        and not st.session_state.awaiting_confirmation
    ):

        if len(agent.belief.asked) >= MAX_QUESTIONS:

            st.session_state.game_over = True
            st.rerun()

        elif agent.belief.probs.max() >= CONFIDENCE_THRESHOLD:

            st.session_state.awaiting_confirmation = True
            st.rerun()

        else:

            if agent.current_question is None:
                question_index = agent.ask()
            else:
                question_index = agent.current_question

            question_text = kb.question_text(question_index)

            st.markdown(
                f"""
                <div class="question-card">
                    <div class="question-label">
                        QUESTION {question_count + 1}
                    </div>
                    <h2>{question_text}</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.form("answer_form"):

                answer_label = st.radio(
                    "Choose your answer:",
                    list(ANSWER_OPTIONS.keys()),
                    horizontal=True
                )

                submitted = st.form_submit_button(
                    "Submit Answer",
                    type="primary",
                    use_container_width=True
                )

                if submitted:

                    answer = ANSWER_OPTIONS[answer_label]

                    agent.receive_answer(answer)

                    if len(agent.belief.asked) >= MAX_QUESTIONS:

                        st.session_state.game_over = True

                    elif agent.belief.probs.max() >= CONFIDENCE_THRESHOLD:

                        st.session_state.awaiting_confirmation = True

                    st.rerun()

    # --------------------------------------------------
    # GUESS CONFIRMATION
    # --------------------------------------------------

    if st.session_state.awaiting_confirmation:

        guess = agent.guess()

        confidence = float(agent.belief.probs.max()) * 100

        st.success("I think I've figured it out!")

        st.subheader(f"Is it {guess.name}?")

        st.write(f"My confidence: **{confidence:.2f}%**")

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✅ Yes, that's correct!",
                type="primary",
                use_container_width=True
            ):

                st.session_state.confirmed_correct = True
                st.session_state.awaiting_confirmation = False
                st.session_state.game_over = True

                st.rerun()

        with col2:

            if st.button(
                "❌ No, try again",
                use_container_width=True
            ):

                agent.confidence_threshold = 1.01

                st.session_state.awaiting_confirmation = False

                if len(agent.belief.asked) >= MAX_QUESTIONS:
                    st.session_state.game_over = True

                st.rerun()

    # --------------------------------------------------
    # GAME RESULTS
    # --------------------------------------------------

    if st.session_state.game_over:

        guess = agent.guess()

        st.divider()

        st.subheader("🏁 Game Finished!")

        if st.session_state.confirmed_correct is True:

            st.success(
                f"🎉 I guessed correctly! Your answer was {guess.name}."
            )

        else:

            st.warning(
                "I couldn't guess your choice within the allowed "
                "number of questions."
            )

            st.markdown(f"### My best guess: {guess.name}")

            st.write(
                f"Confidence: {agent.belief.probs.max() * 100:.2f}%"
            )

            # ------------------------------------------
            # ADD MISSING CANDIDATE
            # ------------------------------------------

            st.divider()

            st.subheader("Help Me Learn!")

            st.write(
                "What were you actually thinking of? "
                "Tell me the correct personality or place so "
                "I can add it to my knowledge base."
            )

            if st.session_state.candidate_added:

                st.success(
                    f"Thank you! **{st.session_state.added_candidate_name}** "
                    "has been added to the knowledge base."
                )

                st.info(
                    "This candidate will be available in future games."
                )

            else:

                with st.form("add_candidate_form"):

                    correct_answer = st.text_input(
                        "Enter the correct personality or place:",
                        placeholder="For example, Abdul Sattar Edhi"
                    )

                    add_submitted = st.form_submit_button(
                        "Add to Knowledge Base",
                        type="primary",
                        use_container_width=True
                    )

                    if add_submitted:
                        add_missing_candidate(correct_answer)
                        st.rerun()

                if st.session_state.add_candidate_error:
                    st.error(st.session_state.add_candidate_error)

        st.info(
            f"Total questions asked: {len(agent.belief.asked)}"
        )

        if st.button(
            "🔄 Play Again",
            type="primary",
            use_container_width=True
        ):

            reset_game()
            st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Powered by Bayesian Belief Updating and Intelligent Question Selection."
)
