import streamlit as st
from basebrawl1 import (
    original_scorpions_players,
    original_aether_players,
    get_new_roster,
    play_full_game
)

# Initialize session state if not already present.
if "game_run" not in st.session_state:
    st.session_state.game_run = False
if "game_log" not in st.session_state:
    st.session_state.game_log = []

st.title("Basebrawl: The Reckoning")
st.markdown("*welcome, mortal...*")

def run_game():
    # Prepare fresh rosters.
    fresh_scorpions_players = get_new_roster(original_scorpions_players)
    fresh_aether_players = get_new_roster(original_aether_players)
    fresh_scorpions_pitchers = fresh_scorpions_players.copy()
    fresh_aether_pitchers = fresh_aether_players.copy()
    # Run the game and store the log in session state.
    st.session_state.game_log = play_full_game(
        fresh_scorpions_players,
        fresh_aether_players,
        fresh_scorpions_pitchers,
        fresh_aether_pitchers,
        "Scorpions", "The Aether"
    )
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
