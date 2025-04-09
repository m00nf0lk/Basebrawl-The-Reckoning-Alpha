import streamlit as st
import random
import re

from Players import get_teams
from basebrawl4 import play_full_game

# --- Session State ---
if "game_run" not in st.session_state:
    st.session_state.game_run = False
if "game_log" not in st.session_state:
    st.session_state.game_log = []

# --- Title & Intro ---
st.title("Basebrawl: The Reckoning")
st.markdown("*welcome back, mortal... the ball knows pain now.*")

def run_game():
    teams = get_teams()
    team_names = list(teams.keys())
    selected_team_names = random.sample(team_names, 2)
    team_a_name, team_b_name = selected_team_names[0], selected_team_names[1]

    team_a_master = teams[team_a_name]
    team_b_master = teams[team_b_name]

    if "flip_order" not in st.session_state:
        st.session_state.flip_order = False

    if st.session_state.flip_order:
        st.session_state.game_log = play_full_game(
            team_b_master, team_a_master,
            team_b_master, team_a_master,
            team_b_name, team_a_name
        )
    else:
        st.session_state.game_log = play_full_game(
            team_a_master, team_b_master,
            team_a_master, team_b_master,
            team_a_name, team_b_name
        )

    st.session_state.flip_order = not st.session_state.flip_order
    st.session_state.game_run = True

# --- Button ---
button_label = "RE-PLAY BALL!" if st.session_state.game_run else "PLAY BALL!"
st.button(button_label, on_click=run_game)

# --- Display Log ---
def reformat_log_line(line: str) -> str:
    pattern = r'(\(B[^)]*\)\s*[🟩⬜]+|\(B[^)]*\)|[🟩⬜]+)'
    line = re.sub(pattern, r'\n\1', line)
    line = re.sub(r'\n+', '\n', line)
    return line.strip()

if st.session_state.game_log:
    for line in st.session_state.game_log:
        formatted_line = reformat_log_line(line)
        st.text(formatted_line)

# --- Conditionally show "Back to Top" button ---
back_to_top_html = """
<style>
.back-to-top {
    text-align: center;
    margin-top: 30px;
}
.back-to-top a {
    background-color: #28a745;
    color: white !important;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
}
.back-to-top a:hover {
    background-color: #218838;
}
</style>
<div class="back-to-top">
    <a href="#basebrawl-the-reckoning">BACK TO TOP</a>
</div>
"""

if st.session_state.game_run:
    st.markdown(back_to_top_html, unsafe_allow_html=True)


# streamlit run App.py
