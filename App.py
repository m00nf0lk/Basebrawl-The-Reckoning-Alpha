import streamlit as st
import random
import re
import pandas as pd  # Importing pandas to handle CSV files

from Players import get_teams  # Returns a deep copy of the master teams.
from basebrawl5 import play_full_game

# --- Page Layout ---
st.set_page_config(
    page_title="Basebrawl: The Reckoning",
    layout="centered",  # Normal layout width
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
st.markdown("*welcome back, mortal... are you horny for the book?*")


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


def toggle_stats():
    """
    Toggle the visibility of the CSV stats.
    When toggled on, load the CSV file without dropping any columns.
    Renaming is done based on the detected number of columns.

    - If the CSV has 9 columns:
         * Keep column 0 unchanged.
         * Rename columns 1-8 to "pow", "agil", "chutz", "bat", "pitch", "base", "field", "brawl".

    - If the CSV has 10 columns:
         * Keep columns 0 and 1 unchanged.
         * Rename columns 2-9 to "pow", "agil", "chutz", "bat", "pitch", "base", "field", "brawl".
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
                new_columns = [df.columns[0], df.columns[1]] + ["pow", "agil", "chutz", "bat", "pitch", "base", "field",
                                                                "brawl"]
                df.columns = new_columns
            else:
                st.error(f"Expected CSV to have 9 or 10 columns; found {num_columns} columns.")
                st.session_state.show_stats = False
                return
            st.session_state.stats_df = df
        except Exception as e:
            st.error("Error loading stats: " + str(e))
            st.session_state.show_stats = False  # Turn off if error occurs


# --- Primary Buttons (Stacked Vertically) ---
button_label = "RE-PLAY BALL!" if st.session_state.game_run else "PLAY BALL!"
st.button(button_label, on_click=run_game)
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
    # Set a custom height for the dataframe display (e.g., 600 pixels)
    st.dataframe(st.session_state.stats_df, height=1200)

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
