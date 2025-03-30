import streamlit as st
from basebrawl1 import (
    original_scorpions_players,
    original_aether_players,
    get_new_roster,
    play_full_game
)

# Add an anchor at the top for scrolling.
st.markdown('<div id="top" style="padding-top: 80px; margin-top: -80px;"></div>', unsafe_allow_html=True)

# Initialize session state if not already present.
if "game_run" not in st.session_state:
    st.session_state.game_run = False
if "game_log" not in st.session_state:
    st.session_state.game_log = []

st.title("Basebrawl: The Reckoning - 3/30")
st.markdown("*welcome, mortal...*")

def run_game():
    # Prepare fresh rosters.
    fresh_scorpions_players = get_new_roster(original_scorpions_players)
    fresh_aether_players = get_new_roster(original_aether_players)
    fresh_scorpions_pitchers = fresh_scorpions_players.copy()
    fresh_aether_pitchers = fresh_aether_players.copy()

    # Initialize flip flag if not present.
    if "flip_order" not in st.session_state:
        st.session_state.flip_order = False

    # If flip_order is True, swap team order.
    if st.session_state.flip_order:
        # Now The Aether bats first.
        st.session_state.game_log = play_full_game(
            fresh_aether_players,
            fresh_scorpions_players,
            fresh_aether_pitchers,
            fresh_scorpions_pitchers,
            "The Aether",   # Team A (batting first)
            "Scorpions"     # Team B (batting second)
        )
    else:
        # Scorpions bat first.
        st.session_state.game_log = play_full_game(
            fresh_scorpions_players,
            fresh_aether_players,
            fresh_scorpions_pitchers,
            fresh_aether_pitchers,
            "Scorpions",    # Team A (batting first)
            "The Aether"    # Team B (batting second)
        )

    # Toggle the flag for the next game.
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


st.markdown(
    """
    <style>
    .scroll-button {
        display: inline-block;
        padding: 0.5em 1em;
        background-color: #4CAF50;
        text-align: center;
        text-decoration: none;
        border-radius: 4px;
        margin-top: 1em;
    }

    a.scroll-button {
    color: white!important
    }
    
    </style>
    <a href="#top" class="scroll-button">GO BACK FROM WHENCE YE CAME</a>
    """,
    unsafe_allow_html=True
)
