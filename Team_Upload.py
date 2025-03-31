import csv
import copy

class Player:
    def __init__(self, name, power, agility, chutzpah, batting, pitching, baserunning, fielding, brawling):
        self.name = name
        self.base_power = power
        self.base_agility = agility
        self.base_chutzpah = chutzpah
        self.base_batting = batting
        self.base_pitching = pitching
        self.base_baserunning = baserunning
        self.base_fielding = fielding
        self.base_brawling = brawling
        self.power = power
        self.agility = agility
        self.chutzpah = chutzpah
        self.batting = batting
        self.pitching = pitching
        self.baserunning = baserunning
        self.fielding = fielding
        self.brawling = brawling
        self.is_dead = False
        self.injury_status = None
        self.injury_debuff = 0
        self.recovery_bonus = 0.0
        self.knockout_halves_remaining = 0
        self.pending_death = False

def load_master_teams(csv_file_path):
    teams = {}
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            team_name = row['Team']
            player = Player(
                name=row['Name'],
                power=int(row['Power']),
                agility=int(row['Agility']),
                chutzpah=int(row['Chutzpah']),
                batting=int(row['Batting']),
                pitching=int(row['Pitching']),
                baserunning=int(row['Baserunning']),
                fielding=int(row['Fielding']),
                brawling=int(row['Brawling'])
            )
            teams.setdefault(team_name, []).append(player)
    return teams

# Load the master teams once at the start.
MASTER_TEAMS = load_master_teams("players.csv")
