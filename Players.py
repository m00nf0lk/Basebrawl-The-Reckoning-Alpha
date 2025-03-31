import copy
from Team_Upload import MASTER_TEAMS, Player  # Importing MASTER_TEAMS and Player for consistency

def get_teams():
    """
    Returns a fresh deep copy of the master teams data.
    This ensures that any modifications during a game do not affect the master copy.
    """
    return copy.deepcopy(MASTER_TEAMS)

# Example usage in your simulator:
if __name__ == "__main__":
    teams = get_teams()
    # List the available team names
    team_names = list(teams.keys())
    # For example, randomly select two teams:
    import random
    selected_team_names = random.sample(team_names, 2)
    team_a = teams[selected_team_names[0]]
    team_b = teams[selected_team_names[1]]
    print("Team A:", [player.name for player in team_a])
    print("Team B:", [player.name for player in team_b])
