import streamlit as st
import random
import copy

# Instead of importing original_scorpions_players, original_aether_players, and get_new_roster,
# we import get_teams (which already returns a fresh deep copy of the master teams)
from Players import get_teams
from basebrawl2 import play_full_game

# Initialize session state if not already present.
if "game_run" not in st.session_state:
    st.session_state.game_run = False
if "game_log" not in st.session_state:
    st.session_state.game_log = []

st.title("Basebrawl: The Reckoning")
st.markdown("*welcome, mortal...*")


def run_game():
    # Load all teams dynamically from Players.py.
    teams = get_teams()  # This returns a fresh deep copy of the master teams.

    # Get available team names and randomly select two teams.
    team_names = list(teams.keys())
    selected_team_names = random.sample(team_names, 2)
    team_a_name = selected_team_names[0]
    team_b_name = selected_team_names[1]

    # Retrieve the rosters for the selected teams.
    team_a_master = teams[team_a_name]
    team_b_master = teams[team_b_name]

    # For separate pitcher lists (if needed), we can use a shallow copy.
    pitchers_a = team_a_master.copy()
    pitchers_b = team_b_master.copy()

    # Initialize flip flag if not present.
    if "flip_order" not in st.session_state:
        st.session_state.flip_order = False

    # If flip_order is True, swap team order (i.e. which team bats first).
    if st.session_state.flip_order:
        # Now Team B (selected second) bats first.
        st.session_state.game_log = play_full_game(
            team_b_master,  # Team B's roster (batting first)
            team_a_master,  # Team A's roster (batting second)
            pitchers_b,  # Pitchers for Team B
            pitchers_a,  # Pitchers for Team A
            team_b_name,  # Team B name (batting first)
            team_a_name  # Team A name (batting second)
        )
    else:
        # Team A bats first.
        st.session_state.game_log = play_full_game(
            team_a_master,  # Team A's roster (batting first)
            team_b_master,  # Team B's roster (batting second)
            pitchers_a,  # Pitchers for Team A
            pitchers_b,  # Pitchers for Team B
            team_a_name,  # Team A name (batting first)
            team_b_name  # Team B name (batting second)
        )

    # Toggle the flip flag for the next game.
    st.session_state.flip_order = not st.session_state.flip_order
    st.session_state.game_run = True


# Determine the button label based on session state.
button_label = "RE-PLAY BALL!" if st.session_state.game_run else "PLAY BALL!"

# Use the on_click parameter to update state immediately on first click.
st.button(button_label, on_click=run_game)

# Display the game log if it exists.
if st.session_state.game_log:
    st.write("### Game Log")
    for line in st.session_state.game_log:
        st.write(line)
