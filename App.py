import streamlit as st
import random
import re
import pandas as pd
from copy import deepcopy  # Import deepcopy to clone teams

from Players import get_teams  # Returns a deep copy of the master teams.
from basebrawl5 import play_full_game

# --- Page Layout ---
st.set_page_config(
    page_title="Basebrawl: The Reckoning",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Session State ---
if "game_run" not in st.session_state:
    st.session_state.game_run = False
if "game_log" not in st.session_state:
    st.session_state.game_log = []
if "stats_df" not in st.session_state:
    st.session_state.stats_df = None
if "show_stats" not in st.session_state:
    st.session_state.show_stats = False

# --- Title & Intro ---
st.title("Basebrawl: The Reckoning")
st.markdown("*welcome back, mortal... craft fates, make clones, scramblerize the universe, whatever.*")

# Retrieve teams once so we have access to the team names.
teams = get_teams()
team_names = list(teams.keys())

# --- Team Selection Dropdowns ---
selected_team_a = st.selectbox("Select Team A", team_names, key="selected_team_a")
selected_team_b = st.selectbox("Select Team B", team_names, key="selected_team_b")

def run_game():
    """
    Runs a game using the teams selected by the user via the dropdowns.
    If the same team is selected for both positions, two independent copies
    are created. For Team A, the display name is updated to include "(CLONES)"
    and each player's name is prefixed with "CLONE ".
    """
    team_a_name = st.session_state.selected_team_a
    team_b_name = st.session_state.selected_team_b

    if team_a_name == team_b_name:
        # Create two independent copies of the chosen team.
        original_team = teams[team_a_name]
        team_a_master = deepcopy(original_team)
        team_b_master = deepcopy(original_team)

        # Update Team A's display name and each player's name.
        display_team_a_name = team_a_name + " (CLONES)"
        for player in team_a_master:
            if isinstance(player, dict) and "name" in player:
                player["name"] = "CLONE " + player["name"]
            elif hasattr(player, "name"):
                player.name = "CLONE " + player.name
    else:
        # If the teams are different, use them directly.
        team_a_master = teams[team_a_name]
        team_b_master = teams[team_b_name]
        display_team_a_name = team_a_name

    if "flip_order" not in st.session_state:
        st.session_state.flip_order = False

    # Use the flip_order logic to alternate game order.
    if st.session_state.flip_order:
        st.session_state.game_log = play_full_game(
            team_b_master, team_a_master,
            team_b_master, team_a_master,
            team_b_name, display_team_a_name
        )
    else:
        st.session_state.game_log = play_full_game(
            team_a_master, team_b_master,
            team_a_master, team_b_master,
            display_team_a_name, team_b_name
        )

    st.session_state.flip_order = not st.session_state.flip_order
    st.session_state.game_run = True

def run_random_game():
    """
    Runs a game using two random teams selected from the available teams.
    This function always uses the teams' original names.
    """
    team_names_random = random.sample(team_names, 2)
    team_a_name = team_names_random[0]
    team_b_name = team_names_random[1]

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

def toggle_stats():
    """
    Toggle the visibility of the CSV stats.
    When toggled on, load the CSV file without dropping any columns.
    Renaming is done based on the detected number of columns.
    """
    st.session_state.show_stats = not st.session_state.show_stats
    if st.session_state.show_stats:
        try:
            df = pd.read_csv("players.csv")
            num_columns = df.shape[1]
            if num_columns == 9:
                new_columns = [df.columns[0]] + ["pow", "agil", "chutz", "bat", "pitch", "base", "field", "brawl"]
                df.columns = new_columns
            elif num_columns == 10:
                new_columns = [df.columns[0], df.columns[1]] + ["pow", "agil", "chutz", "bat", "pitch", "base", "field", "brawl"]
                df.columns = new_columns
            else:
                st.error(f"Expected CSV to have 9 or 10 columns; found {num_columns} columns.")
                st.session_state.show_stats = False
                return
            st.session_state.stats_df = df
        except Exception as e:
            st.error("Error loading stats: " + str(e))
            st.session_state.show_stats = False  # Turn off if error occurs

# --- Primary Buttons ---
st.button("PLAY BALL!", on_click=run_game)
st.button("SCRAMBLERIZER", on_click=run_random_game)
st.button("THE GRIMOIRE", on_click=toggle_stats)

# --- Display Game Log ---
def reformat_log_line(line: str) -> str:
    pattern = r'(\(B[^)]*\)\s*[🟩⬜]+|\(B[^)]*\)|[🟩⬜]+)'
    line = re.sub(pattern, r'\n\1', line)
    line = re.sub(r'\n+', '\n', line)
    return line.strip()

if st.session_state.game_log:
    for line in st.session_state.game_log:
        formatted_line = reformat_log_line(line)
        st.text(formatted_line)

# --- Conditionally Display CSV Stats Below Game Log ---
if st.session_state.show_stats and st.session_state.stats_df is not None:
    st.subheader("Player Stats")
    st.dataframe(st.session_state.stats_df, height=1200)

# --- "Back to Top" Button ---
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
