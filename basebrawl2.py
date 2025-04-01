import random
import copy

# ------------------ Updated Team Loading Block ------------------
# Import get_teams from Players.py (which returns a fresh deep copy of MASTER_TEAMS)
from Players import get_teams

# Get all teams from Players.py (already deep-copied)
teams = get_teams()

# Extract available team names from the dictionary keys
team_names = list(teams.keys())

# Randomly select two teams from the available teams
selected_team_names = random.sample(team_names, 2)
team_a_name = selected_team_names[0]
team_b_name = selected_team_names[1]

# Retrieve the rosters for these teams (they are already fresh deep copies)
team_a_master = teams[team_a_name]
team_b_master = teams[team_b_name]

# If you need separate pitcher lists, a shallow copy is sufficient:
pitchers_a = team_a_master.copy()
pitchers_b = team_b_master.copy()
# -------------------------------------------------------------------

def update_player_stats(player):
    """
    Recalculate a player's current stats from their base values minus the current injury debuff.
    """
    player.power       = max(0, player.base_power - player.injury_debuff)
    player.agility     = max(0, player.base_agility - player.injury_debuff)
    player.chutzpah    = max(0, player.base_chutzpah - player.injury_debuff)
    player.batting     = max(0, player.base_batting - player.injury_debuff)
    player.pitching    = max(0, player.base_pitching - player.injury_debuff)
    player.baserunning = max(0, player.base_baserunning - player.injury_debuff)
    player.fielding    = max(0, player.base_fielding - player.injury_debuff)
    player.brawling    = max(0, player.base_brawling - player.injury_debuff)


#===== Foul Mood =====#

class FoulMood:
    BONUS_TIERS = [0, 10, 25, 50, 80]
    BONUS_MESSAGES = {
        10: "Both teams are in a Foul Mood. 🐔",
        25: "Both teams are in a Very Foul Mood. 🐔🐔",
        50: "Both teams are in an Extremely Foul Mood. 🐔🐔🐔",
        80: "Both teams are in the DANKEST OF FOUL MOODS!!! 🐔🐔🐔🐔"
    }

    def __init__(self):
        self.bonus = 0
        self.consecutive = 0
        self.last_pitch_was_foul = False

    def update(self, is_foul):
        if is_foul:
            if self.last_pitch_was_foul:
                self.consecutive += 1
                if self.bonus >= self.BONUS_TIERS[-1]:
                    increased = False
                else:
                    current_index = self.BONUS_TIERS.index(self.bonus) if self.bonus in self.BONUS_TIERS else 0
                    if current_index < len(self.BONUS_TIERS) - 1:
                        new_bonus = self.BONUS_TIERS[current_index + 1]
                        if new_bonus > self.bonus:
                            self.bonus = new_bonus
                            increased = True
                        else:
                            increased = False
                    else:
                        increased = False
            else:
                self.consecutive = 1
                increased = False
            self.last_pitch_was_foul = True
            return increased
        else:
            self.last_pitch_was_foul = False
            return False

    def get_bonus_message(self):
        return self.BONUS_MESSAGES.get(self.bonus, f"Foul Mood = {self.bonus}")

    def reset_per_atbat(self):
        """Reset the at-bat specific consecutive foul count and flag,
        leaving the persistent bonus intact."""
        self.consecutive = 0
        self.last_pitch_was_foul = False

    def reset(self):
        """Fully reset foul mood for a new game (bonus and at-bat state)."""
        self.bonus = 0
        self.consecutive = 0
        self.last_pitch_was_foul = False

#===== Riled Up =====#

def apply_riled_buff(team, bonus):
    """
    Apply a flat bonus to all eight stats of every player on the team.
    The function checks if the player already has a buff and updates accordingly.
    """
    for player in team:
        if not hasattr(player, 'riled_buff'):
            player.riled_buff = 0
        diff = bonus - player.riled_buff
        player.power       += diff
        player.agility     += diff
        player.chutzpah    += diff
        player.batting     += diff
        player.pitching    += diff
        player.baserunning += diff
        player.fielding    += diff
        player.riled_buff = bonus

def remove_riled_buff(team):
    """
    Remove any applied riled buff from each player, restoring their base stats.
    """
    for player in team:
        if hasattr(player, 'riled_buff'):
            bonus = player.riled_buff
            player.power       -= bonus
            player.agility     -= bonus
            player.chutzpah    -= bonus
            player.batting     -= bonus
            player.pitching    -= bonus
            player.baserunning -= bonus
            player.fielding    -= bonus
            player.brawling    -= bonus
            player.riled_buff = 0

class RiledUp:
    """
    Manages the "riled up" state for a team.
    This state is a comeback mechanic; the higher the tier (from 0 to MAX_TIER),
    the greater the bonus the team receives. Various game events can trigger changes
    in the riled up state.
    """
    MAX_TIER = 5

    # Basic message when simply checking the current state.
    BONUS_MESSAGES = {
        0: "{team_name} are calm.",
        1: "{team_name} are getting Riled Up! 🔥",
        2: "{team_name} are getting Riled Up! 🔥🔥",
        3: "{team_name} are getting Riled Up! 🔥🔥🔥",
        4: "{team_name} are getting Riled Up! 🔥🔥🔥🔥",
        5: "{team_name} are getting Riled Up! 🔥🔥🔥🔥🔥"
    }

    @staticmethod
    def riled_fires(tier: int) -> str:
        """
        Returns a string of '🔥' repeated 'tier' times.
        For tier=3, returns '🔥🔥🔥'.
        """
        return "🔥" * tier

    def __init__(self):
        # Initialize the riled up tier to 0 (no bonus)
        self.tier = 0

    def increase(self, amount=1):
        """
        Increase the riled up tier by a given amount.
        The tier is capped at MAX_TIER.
        """
        self.tier += amount
        if self.tier > self.MAX_TIER:
            self.tier = self.MAX_TIER

    def decrease(self, amount=1):
        """
        Decrease the riled up tier by a given amount.
        The tier will not drop below 0.
        """
        self.tier = max(0, self.tier - amount)

    def reset(self):
        """
        Reset the riled up tier back to 0.
        """
        self.tier = 0

    def get_bonus(self):
        """
        Returns the bonus value based on the current tier.
        For this example, the bonus is equal to the tier.
        """
        return (self.tier * 2)

    def get_message(self, team_name):
        """
        Returns the base message for the current riled up state.
        """
        return self.BONUS_MESSAGES.get(self.tier, "{team_name} has an unknown riled up state.").format(team_name=team_name)

    # --- Trigger Methods for Different Game Events ---

    def trigger_by_deficit(self, runs_deficit, team_name):
        """
        Triggered when a team is behind by 5 or more runs at the end of a half-inning.
        Increases the tier by 1 and returns a message reflecting that the team is becoming more riled up.
        """
        if runs_deficit >= 3:
            self.increase(1)
            bonus_message = self.get_message(team_name)
            return f"Falling behind by {runs_deficit} runs, {bonus_message}"
        return ""

    def reduce_on_score(self, team_name):
        """
        Triggered whenever a team scores a point.
        If the team is riled up (tier > 0), the tier drops by 1.
        Returns a message indicating that the team's riled up state has been reduced.
        """
        if self.tier > 0:
            self.decrease(1)
            if self.tier == 0:
                # Tier went all the way down
                return f"Scoring points soothes {team_name}'s frustration completely. Riled all the way down. 💧"
            else:
                # Tier is now 1..4 (or up to 5 if you allow it)
                # Show a line with "Riled down to X fires"
                return f"Scoring points calms {team_name}'s frustration. Riled down to {RiledUp.riled_fires(self.tier)}"
        return ""

# ===== Helper Functions ===== #

# Check if a team is empty #
def is_team_empty(team):
    """Return True if the team has no players (i.e. all players are dead/removed)."""
    return len(team) == 0

def display_bases_as_squares(base_runners):
    third_base = "🟩" if base_runners[2] else "⬜"
    second_base = "🟩" if base_runners[1] else "⬜"
    first_base = "🟩" if base_runners[0] else "⬜"
    return f"{third_base}{second_base}{first_base}"

#unused
def verb_for_team(team_name, singular="gets", plural="get"):
    # If the team name ends with "s" assume it's plural.
    return plural if team_name.endswith("s") else singular

#unused
def becomes_for_team(team_name, singular="becomes", plural="become"):
    # Similarly, choose between "becomes" and "become".
    return plural if team_name.endswith("s") else singular

def base_number_to_text(base_index):
    mapping = {0: "first base", 1: "second base", 2: "third base"}
    return mapping.get(base_index, "home plate")

def format_bso(balls, strikes, outs):
    ball_display = f"B{'-' if balls == 0 else balls}"
    strike_display = f"S{'-' if strikes == 0 else strikes}"
    out_display = f"O{'-' if outs == 0 else outs}"
    return f"({ball_display}/{strike_display}/{out_display})"

def format_player_status(player):
    """
    Returns the player's name along with any active status (e.g., Winded, Shook Up, Injured).
    Also includes if the player is knocked out or dead.
    """
    base_name = player.name
    statuses = []
    # Include injury statuses if present.
    if hasattr(player, "injury_status") and player.injury_status in ["Winded", "Shook Up", "Injured"]:
        statuses.append(f"{player.injury_status}")
    # Also include knocked out or dead statuses.
    if getattr(player, "pending_death", False):
        # Do not show "dead" yet; you might choose to show "critically injured" or simply nothing.
        statuses.append("")
    elif getattr(player, "is_dead", False):
        statuses.append("dead")
    #--- "knockout_halves_remaining" is old but not causing any harm, rework one day.
    elif hasattr(player, "knockout_halves_remaining") and player.knockout_halves_remaining > 0:
        statuses.append("knocked out")
    if statuses:
        return f"{base_name} ({'; '.join(statuses)})"
    else:
        return base_name

def remove_dead_from_bases(base_runners):
    """
    Iterates over the list of base runners (positions for first, second, and third)
    and sets any runner who is not active (i.e. dead or knocked out) to None.
    """
    return [runner if (runner is not None and is_active(runner)) else None for runner in base_runners]

def finalize_pending_deaths(team):
    """
    Iterates over the team and, for any player flagged as pending death,
    sets them as dead and removes the pending flag.
    """
    for player in team:
        if getattr(player, "pending_death", False):
            player.is_dead = True
            player.final_bat_allowed = True
            del player.pending_death

#=== Position Assignments ===#

def is_active(player):
    """
    Determines if a player is active.
    A player is active if they are not dead and not knocked out.
    """
    if getattr(player, "is_dead", False) and not getattr(player, "final_bat_allowed", False):
        return False
    if hasattr(player, "knockout_halves_remaining") and player.knockout_halves_remaining > 0:
        return False
    return True

def assign_defensive_positions(roster):
    """
    Randomly assigns defensive positions from the full roster.
    All players (dead, knocked out, or active) are assigned to a position,
    so that their status can be logged (e.g., "Dread Malakar is dead").
    (Note: The pitcher is handled separately and must be active.)
    """
    roster_copy = roster.copy()
    random.shuffle(roster_copy)

    positions = {
        "catcher": roster_copy.pop() if roster_copy else None,
        "first_base": roster_copy.pop() if roster_copy else None,
        "second_base": roster_copy.pop() if roster_copy else None,
        "third_base": roster_copy.pop() if roster_copy else None,
        "shortstop": roster_copy.pop() if roster_copy else None,
        "left_field": roster_copy.pop() if roster_copy else None,
        "center_field": roster_copy.pop() if roster_copy else None,
        "right_field": roster_copy.pop() if roster_copy else None,
    }
    # Do not remove players who are dead or knocked out.
    # This allows the game to log their status while they contribute 0 to defensive rolls.
    return positions

def select_pitcher(team):
    """
    Selects a pitcher from the team.
    The pitcher must be active.
    """
    active_pitchers = [p for p in team if is_active(p)]
    return random.choice(active_pitchers) if active_pitchers else None

def batter_status_message(batter, team_name):
    if getattr(batter, "is_dead", False):
        if getattr(batter, "final_bat_allowed", False):
            batter.final_bat_allowed = False  # Use their final appearance now
            return f"{batter.name} was called to the plate... but they're dead."
        else:
            return None
    elif hasattr(batter, "knockout_halves_remaining") and batter.knockout_halves_remaining > 0:
        return f"{batter.name} was called to the plate... but they're knocked out."
    elif hasattr(batter, "injury_status") and batter.injury_status in ["Winded", "Shook Up", "Injured"]:
        # Use the helper to show the status but still keep the context of stepping up.
        return f"{format_player_status(batter)} steps up to the plate, batting for {team_name}!"
    else:
        return f"{format_player_status(batter)} steps up to the plate, batting for {team_name}!"

#==== Advancement and Fielding ====#

def calculate_runner_score(runner):
    return runner.baserunning

def calculate_fielder_score(fielder):
    # If the fielder is dead or knocked out, return 0 so they don't contribute to defensive rolls.
    if fielder is None or not is_active(fielder):
        return 0
    return fielder.fielding

def baserunning_roll(runner, fielder):
    roll = random.randint(1, 100)
    total_roll = roll + (calculate_runner_score(runner) - calculate_fielder_score(fielder))
    if total_roll >= 90:
        return "extra_base", total_roll
    elif total_roll >=  45:
        return "safe", total_roll
    elif total_roll == 44:
        return "close_tag_out", total_roll
    elif total_roll == 43:
        return "collision", total_roll
    else:
        return "tag_out", total_roll

def resolve_extra_bases():
    # Determine how many extra bases to advance using the 85/14/1 breakdown
    extra_roll = random.randint(1, 100)
    if extra_roll <= 85:
        return 1
    elif extra_roll <= 85 + 14:
        return 2
    else:
        return 3

# --- Updated get_fielder_for_base ---
position_names = {
    "first_base": "first base",
    "second_base": "second base",
    "third_base": "third base",
    "catcher": "catcher",
    "left_field": "left fielder",
    "center_field": "center fielder",
    "right_field": "right fielder"
}

position_abbr = {
    "left_field": "left fielder",
    "center_field": "center fielder",
    "right_field": "right fielder"
}

def get_fielder_for_base(base, defensive_positions):
    primary_status_message = ""
    if base == 0:
        primary_position = "first_base"
    elif base == 1:
        primary_position = "second_base"
    elif base == 2:
        primary_position = "third_base"
    else:
        primary_position = "catcher"
    expected_fielder = defensive_positions.get(primary_position)

    if expected_fielder is not None and is_active(expected_fielder):
        primary_status = "active"
    else:
        if expected_fielder is not None:
            if getattr(expected_fielder, "is_dead", False):
                primary_status_message = f"{expected_fielder.name} is dead"
            elif hasattr(expected_fielder, "knockout_halves_remaining") and expected_fielder.knockout_halves_remaining > 0:
                primary_status_message = f"{expected_fielder.name} is knocked out"
            else:
                primary_status_message = f"{format_player_status(expected_fielder)} is on defense"
        primary_status = "inactive"

#==== Assists ====#
    assist_fielder = None
    assist_position = None
    assist_info = ""

    outfield_candidates = []
    for pos in ["left_field", "center_field", "right_field"]:
        p = defensive_positions.get(pos)
        if p is not None and is_active(p):
            outfield_candidates.append((p, pos))

    if outfield_candidates:
        candidate, candidate_position = random.choice(outfield_candidates)
        assist_attempt_probability = max(candidate.agility / 10.0, 0.05)
        if random.random() <= assist_attempt_probability:
            assist_roll = random.randint(1, 100) + candidate.agility
            primary_roll = random.randint(1, 100) if primary_status == "active" else 0
            if assist_roll > primary_roll:
                assist_fielder = candidate
                assist_position = candidate_position
                abbr = position_abbr.get(candidate_position, candidate_position)
                assist_info = f"Great assist by {candidate.name}!"
            else:
                assist_info = f""

    return expected_fielder, primary_position, primary_status_message, assist_fielder, assist_position, assist_info

def attempt_base_advancement(runner, current_base, target_base, defensive_positions, occupied_bases, frozen_bases,
                             is_top, score, team_a_name, team_b_name, team_a, team_b,
                             foul_mood, riled_up, final_bso, outs, allow_extra=True):
    runner_movements = []
    runs_scored = 0
    play_by_play_message = []
    batting_team = team_a_name if is_top else team_b_name
    # new_base will hold the base index (0,1,2) that the runner occupies if safe.
    # If the runner scores (target_base == 3) or is out, new_base remains None.
    new_base = None

    # Immediately check if the target base is frozen.
    if frozen_bases.get(target_base, False):
        return ("frozen", runner_movements, runs_scored, play_by_play_message, outs, new_base)

    # Retrieve defender info for the target base.
    (expected_fielder, primary_position, primary_status_message,
     assist_fielder, assist_position, assist_info) = get_fielder_for_base(target_base, defensive_positions)
    active_defender = assist_fielder if assist_fielder is not None else expected_fielder

    # If no active defender is present, the runner advances safely.
    if not is_active(active_defender):
        # Build a message that varies based on whether the runner is going home.
        if target_base == 3:
            msg = f"{format_player_status(runner)} freely advances to home plate and scores"
        else:
            msg = f"{format_player_status(runner)} freely advances to {base_number_to_text(target_base)}"
        if primary_status_message:
            msg += f" because {primary_status_message}"
        msg += "!"
        runner_movements.append(msg)

        if target_base == 3:
            if outs < 3:
                runs_scored += 1
                if is_top:
                    score[team_a_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_a_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_a, bonus)
                else:
                    score[team_b_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_b_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_b, bonus)
                play_by_play_message.append(
                    f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                )
                # Runner scores; new_base remains None.
                return ("score", runner_movements, runs_scored, play_by_play_message, outs, None)
        else:
            # For bases 0-2, set new_base accordingly.
            new_base = target_base if target_base in (0, 1, 2) else None
            return ("safe", runner_movements, runs_scored, play_by_play_message, outs, new_base)

    # Otherwise, perform the baserunning roll.
    roll_result, total_roll = baserunning_roll(runner, active_defender)
    #if not allow_extra and roll_result == "extra_base":
        #roll_result = "safe"
    if primary_status_message:
        runner_movements.append(primary_status_message)

    # --- Outcome: Extra Base ---
    if roll_result == "extra_base":
        # If the runner is already on third (target_base == 3), no extra base advancement is applied;
        # simply score the runner.
        starting_base = target_base if target_base == 0 else target_base - 1
        if target_base == 3:
            if outs < 3:
                runs_scored += 1
                runner_movements.append(f"{format_player_status(runner)} scores!")
                if is_top:
                    score[team_a_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_a_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_a, bonus)
                else:
                    score[team_b_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_b_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_b, bonus)
                play_by_play_message.append(
                    f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                )
            new_base = target_base
            return ("score", runner_movements, runs_scored, play_by_play_message, outs, new_base)

        # Otherwise, calculate the extra base target.
        if target_base != 3:
            extra_target = target_base + 1 if target_base < 2 else 3
        else:
            extra_target = 3

        if occupied_bases.get(extra_target) is not None or frozen_bases.get(extra_target, False):
            new_target = target_base
        else:
            new_target = extra_target
            if new_target != 3:
                runner_movements.append(
                    f"{format_player_status(runner)} takes an extra base from {base_number_to_text(starting_base)} "
                    f"and ends up on {base_number_to_text(new_target)}!"
                )

        # If the new target is home (3), update scoring.
        if new_target == 3:
            if outs < 3:
                runs_scored += 1
                runner_movements.append(f"{format_player_status(runner)} takes an extra base from "
                                        f"{base_number_to_text(starting_base)} and scores!")
                if is_top:
                    score[team_a_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_a_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_a, bonus)
                else:
                    score[team_b_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_b_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_b, bonus)
                play_by_play_message.append(
                    f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                )
            return ("score", runner_movements, runs_scored, play_by_play_message, outs, new_target)
        else:
            new_base = new_target if new_target in (0, 1, 2) else None
            return ("safe", runner_movements, runs_scored, play_by_play_message, outs, new_base)

    # --- Outcome: Safe Advance ---
    elif roll_result == "safe":
        if target_base == 3:
            if outs < 3:
                runs_scored += 1
                runner_movements.append(f"{format_player_status(runner)} scores!")
                if is_top:
                    score[team_a_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_a_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_a, bonus)
                else:
                    score[team_b_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_b_name)
                    if reduce_msg:
                        play_by_play_message.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_b, bonus)
                play_by_play_message.append(
                    f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                )
                return ("score", runner_movements, runs_scored, play_by_play_message, outs, new_base)
        else:
            new_base = target_base if target_base in (0, 1, 2) else None
            return ("safe", runner_movements, runs_scored, play_by_play_message, outs, new_base)

    # --- Outcome: Collision ---
    elif roll_result == "collision":
        base_text = base_number_to_text(target_base)
        if random.random() < 0.5:
            # Safe advancement: no injury processing here.
            runner_movements.append(
                f"{format_player_status(runner)} collides with {format_player_status(active_defender)} but reaches {base_text} safely!"
            )
            new_base = target_base if target_base in (0, 1, 2) else None
            return ("safe", runner_movements, runs_scored, play_by_play_message, outs, new_base)
        else:
            # Out on collision.
            outs += 1
            updated_bso = format_bso(0, 0, outs)
            collision_message = (
                f"{format_player_status(runner)} collides with {format_player_status(active_defender)} and is tagged out at {base_text}!"
            )
            frozen_bases[target_base] = True
            new_base = None
            knockout_message = ""
            angry_message = ""
            # Process injury chance
            injury_chance = 0.4
            if target_base == 2:
                injury_chance += 0.2
            elif target_base == 3:
                injury_chance += 0.4
            if random.random() < injury_chance:
                # Determine which player is injured.
                injured_player = active_defender if random.random() < 0.75 else runner
                apply_injury_to_player(injured_player, "Collision Injury", team_a if injured_player == runner else team_b)
                # If the injured player is the defender (team_b), append extra text and possibly trigger a brawl.
                if injured_player == active_defender:
                    angry_message = "The defense is angry..."
                    maybe_trigger_brawl("collision", team_a, team_b, team_a_name, team_b_name, play_by_play_message, foul_mood)
                knockout_message = f"{injured_player.name} is knocked out from the collision!"
            runner_movements.append(collision_message)
            if knockout_message:
                runner_movements.append(knockout_message)
            if angry_message:
                runner_movements.append(angry_message)
            return ("collision_out", runner_movements, runs_scored, play_by_play_message, outs, new_base)

    # --- Outcome: Close Call ---
    elif roll_result == "close_tag_out":
        base_text = base_number_to_text(target_base)
        outs += 1
        updated_bso = format_bso(0, 0, outs)
        runner_movements.append(
            f"It's a close call, but {format_player_status(runner)} is tagged out at {base_text}! The offense is brooding... {updated_bso}"
        )
        frozen_bases[target_base] = True
        new_base = None
        maybe_trigger_brawl("close_tag_out", team_a, team_b, team_a_name, team_b_name, play_by_play_message, foul_mood)
        return ("close_call_out", runner_movements, runs_scored, play_by_play_message, outs, new_base)

    # --- Outcome: Outs ---
    else:
        outs += 1
        base_text = base_number_to_text(target_base)
        if assist_fielder is not None and expected_fielder is not None:
            message = (f"{position_names.get(assist_position, assist_position).capitalize()} {assist_fielder.name} fires a quick pass to "
                       f"{format_player_status(expected_fielder)} at {base_text}. {format_player_status(runner)} is out!")
            if assist_info:
                message += f" {assist_info}"
            runner_movements.append(message)
        else:
            runner_movements.append(f"{format_player_status(runner)} is tagged out at {base_text}!")
        frozen_bases[target_base] = True
        new_base = None
        return ("tag_out", runner_movements, runs_scored, play_by_play_message, outs, new_base)

#===== Baserunning ===== #
def process_hit_with_correct_base_running(
    batter,
    potential_hit,  # expects strings like "potential_single", "potential_double", etc.
    base_runners,   # list: index 0 = runner on first, 1 = second, 2 = third
    is_top,
    team_a_name,
    team_b_name,
    defensive_positions,
    score,
    team_a,
    team_b,
    foul_mood,
    riled_up,
    final_bso,
    outs
):

    allow_extra = True

    # --- New check to bypass processing if outcome is not a potential hit ---
    if not (potential_hit.startswith("potential_") or potential_hit == "home run"):
        # Outcome was something like "out", "fly out", etc.
        # Ensure the batter is removed from the bases (if present) and return the current state unchanged.
        return (base_runners, 0, [], "", [], [], 0)

    # If the half-inning is over, return early.
    if outs >= 3:
        return (base_runners, 0, [], "", [], [], 0)

    # --- Special Handling for Home Runs (when potential_hit is "home run") ---
    if potential_hit == "home run":
        # Calculate scoring runners: every base runner plus the batter scores.
        scoring_runners = sum(1 for r in base_runners if r is not None) + 1
        runners_scoring = [r.name for r in base_runners if r is not None] + [batter.name]
        # Update the score if outs < 3
        if outs < 3:
            if is_top:
                score[team_a_name] += scoring_runners
            else:
                score[team_b_name] += scoring_runners
        # Clear the bases
        updated_bases = [None, None, None]
        batter_movement = ""
        # Build the riled-down message by calling reduce_on_score
        if is_top:
            riled_message = riled_up.reduce_on_score(team_a_name)
        else:
            riled_message = riled_up.reduce_on_score(team_b_name)
        # Build the current score update string.
        score_update = f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
        # Call the refactored describe_full_play to get the full message.
        play_description, event = describe_full_play(
            batter,
            "home run",
            [],
            batter_movement,
            updated_bases,
            runners_scoring,
            format_bso(0, 0, outs),
            score_update,
            riled_message
        )
        play_by_play_message = [play_description]
        return (updated_bases, scoring_runners, [], batter_movement, play_by_play_message, runners_scoring, 0)

    # --- Determine Intended Advancement Based on Potential Hit ---
    # Base numbering: 0 = first, 1 = second, 2 = third, 3 = home plate.
    if potential_hit == "potential_single" or potential_hit == "potential_bunt_hit":
        intended_targets = {2: 3, 1: 2, 0: 1}  # runners: 3rd->home, 2nd->third, 1st->second
        batter_target = 0  # batter reaches first
    elif potential_hit == "potential_double":
        intended_targets = {2: 3, 1: 3, 0: 2}  # 3rd->home, 2nd->home, 1st->second
        batter_target = 1  # batter reaches second
    elif potential_hit == "potential_triple":
        intended_targets = {2: 3, 1: 3, 0: 3}  # all runners attempt to score (target = home)
        batter_target = 2  # batter reaches third
    else:
        # Default to single if potential_hit is unrecognized.
        intended_targets = {2: 3, 1: 2, 0: 1}
        batter_target = 0

    # --- Initialize Base State ---
    # Map current base runners to base indices (0: first, 1: second, 2: third).
    occupied_bases = {0: None, 1: None, 2: None, 3: None}
    frozen_bases = {0: False, 1: False, 2: False, 3: False}

    # We'll accumulate runner messages with sequence numbers.
    ordered_runner_msgs = []          # list of (sequence, message)
    seq_counter = 0                   # sequence counter for ordering
    play_by_play_message = []         # Additional messages (score updates, etc.)
    runners_scoring = []              # List of names for runners who score
    scoring_runners = 0

    # Create a new dictionary for updated bases (indices 0,1,2)
    new_bases = {0: None, 1: None, 2: None}

    # --- Process Runners in Reverse Order ---
    # Process runner on third (base index 2), then second (1), then first (0)
    frozen_bases = {0: False, 1: False, 2: False, 3: False}
    for base_index in [2, 1, 0]:
        runner = base_runners[base_index]
        if runner is None:
            continue

        # Determine intended target for this runner.
        intended_target = intended_targets.get(base_index)
        if intended_target == 3 and frozen_bases[3]:
            intended_target = 2
        if intended_target == 2 and frozen_bases[2]:
            intended_target = 1
        if intended_target == 1 and frozen_bases[1]:
            intended_target = 0

        outcome, msgs, runs, pbp, outs, new_base = attempt_base_advancement(
            runner, base_index, intended_target, defensive_positions,
            occupied_bases, frozen_bases, is_top, score, team_a_name, team_b_name,
            team_a, team_b, foul_mood, riled_up, final_bso, outs, allow_extra=allow_extra
        )

        for msg in msgs:
            ordered_runner_msgs.append((seq_counter, msg))
            seq_counter += 1

        scoring_runners += runs
        if outcome == "score":
            runners_scoring.append(runner.name)
            # Runner scored; do not occupy any base.
            # Optionally, clear the base from new_bases (it should be None anyway).
        elif outcome == "safe":
            # If new_base is provided (i.e. 0,1,2), then place the runner there.
            if new_base is not None:
                new_bases[new_base] = runner
            else:
                # If no new_base was returned, keep the runner at his original base.
                new_bases[base_index] = runner
        elif outcome in ("frozen", "knocked out"):
            # Runner is not on base.
            pass

        play_by_play_message.extend(pbp)
        # Also update the occupied_bases dictionary if needed:
        # (This may be used for defenders; however, new_bases is what we'll use for base occupancy.)
        if outcome == "safe":
            occupied_bases[intended_target] = runner
        else:
            occupied_bases[base_index] = None

    # Now extract the runner messages in order.
    runner_movements = [msg for seq, msg in sorted(ordered_runner_msgs, key=lambda x: x[0])]

    # Adjust batter_target based on frozen bases.
    if batter_target == 3 and frozen_bases[3]:
        batter_target = 2
    if batter_target == 2 and frozen_bases[2]:
        batter_target = 1
    if batter_target == 1 and frozen_bases[1]:
        batter_target = 0

    # --- Assign Batter's Advancement ---
    if potential_hit not in ["home run", "near_miss_hr"]:
        new_bases[batter_target] = batter
        if batter_target == 0:
            batter_movement = "reaching first base"
        elif batter_target == 1:
            batter_movement = "reaching second base"
        elif batter_target == 2:
            batter_movement = "reaching third base"
        else:
            batter_movement = "scores"
    else:
        # For home run events, you might want to pass an empty string.
        batter_movement = ""

    # --- Final Event Determination ---
    # Remove the "potential_" prefix to derive the basic hit type.
    final_event = potential_hit.replace("potential_", "")
    # If outcomes forced a downgrade (for example, batter on double ended up on first instead of second),
    # adjust the final event accordingly.
    if potential_hit == "potential_double" and batter_target != 1:
        final_event = "single"
    elif potential_hit == "potential_triple" and batter_target != 2:
        final_event = "double"

    # Use the current value of outs to build the final BSO display.
    final_bso_display = format_bso(0, 0, outs)
    # Convert new_bases to a list [first, second, third]
    new_base_runners = [new_bases[0], new_bases[1], new_bases[2]]
    play_description, new_event = describe_full_play(
         batter,
         final_event,
         runner_movements,
         batter_movement,
         new_base_runners,
         runners_scoring,
         final_bso_display
    )

    play_by_play_message.insert(0, play_description)

    return (new_base_runners,
            scoring_runners,
            runner_movements,
            batter_movement,
            play_by_play_message,
            runners_scoring,
            outs)

#==== At-Bat Start ====

#==== pickoff attempt ====
def attempt_pickoff(runner, pitcher):
    attempt_probability = max(pitcher.agility / 25, 0.02)
    if random.random() >= attempt_probability:
        return "no_attempt", 0
    pitcher_score = max(pitcher.pitching, pitcher.agility)
    roll = random.randint(1, 100) + (pitcher_score - runner.baserunning)
    if roll >= 80:
        outcome = "picked_off"
    elif roll >= 30:
        outcome = "checked"
    elif roll >= 10:
        outcome = "fail"
    else:
        outcome = "balk"
    return outcome, roll

def process_pickoff_attempts(base_runners, pitcher, play_by_play_log, score, is_top, team_a_name,
                             team_b_name, defensive_positions, balls, strikes, outs, riled_up, team_a, team_b):
    """
    Iterates over base runners and attempts a pickoff.
    Adjusts base_runners and outs or score depending on the outcome.
    """
    end_at_bat = False
    for base_index in [0, 1, 2]:
        runner = base_runners[base_index]
        if runner is not None and is_active(runner):
            result, roll = attempt_pickoff(runner, defensive_positions.get("pitcher"))
            base_text = base_number_to_text(base_index)
            if result == "picked_off":
                base_runners[base_index] = None
                outs += 1
                updated_bso = format_bso(balls, strikes, outs)
                play_by_play_log.append(f"⚾ {pitcher.name} spins around and throws to {base_text}... OUT! "
                                        f"{format_player_status(runner)} is picked off! {updated_bso}")
                if outs >= 3:
                    end_at_bat = True
                    break

            elif result == "checked":
                updated_bso = format_bso(balls, strikes, outs)
                play_by_play_log.append(f"⚾ {pitcher.name} throws to {base_text} for a pickoff! {format_player_status(runner)} "
                                        f"runs back just in time. Safe!")
            elif result == "balk":
                new_bases = [None, None, None]
                scored = False
                scoring_runner_name = ""
                # If there's a runner on third, they score.
                if base_runners[2] is not None:
                    scored = True
                    scoring_runner_name = base_runners[2].name
                    if is_top:
                        score[team_a_name] += 1
                    else:
                        score[team_b_name] += 1
                # Advance runners: runner on second moves to third, runner on first moves to second.
                new_bases[2] = base_runners[1]
                new_bases[1] = base_runners[0]
                base_runners = new_bases
                if scored:
                    # (1) Action message:
                    play_by_play_log.append(
                        f"{pitcher.name} slips up on the mound... and it's a balk! All baserunners advance. {scoring_runner_name} scores! {display_bases_as_squares(base_runners)}"
                    )
                    # (2) Riled-down message:
                    if is_top:
                        reduce_msg = riled_up.reduce_on_score(team_a_name)
                    else:
                        reduce_msg = riled_up.reduce_on_score(team_b_name)
                    if reduce_msg:
                        play_by_play_log.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        if is_top:
                            apply_riled_buff(team_a, bonus)
                        else:
                            apply_riled_buff(team_b, bonus)
                    # (3) Current score update:
                    score_line = f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                    play_by_play_log.append(score_line)
                else:
                    play_by_play_log.append(
                        f"{pitcher.name} slips up on the mound... and it's a balk! All baserunners advance. {display_bases_as_squares(base_runners)}"
                    )

            elif result == "no_attempt":
                pass
    return base_runners, score, outs, end_at_bat

def at_bat_with_pitch_sequence(batter, pitcher, base_runners, current_outs, defensive_positions,
                               is_top, team_a_name, team_b_name, score, team_a, team_b, riled_up,
                               declared=True, foul_mood=None):
    """
    Process an at-bat pitch-by-pitch. In this reworked version, we delay the termination of the pitch loop
    when the third out is reached, so that we can log all events leading up to that moment.
    """
    # Initialize a pitch counter at the start of the at-bat
    pitch_count = 0

    if foul_mood is None:
        foul_mood = FoulMood()  # Create a new instance if none is passed in

    # Reset the at-bat consecutive foul state (but leave bonus intact)
    foul_mood.reset_per_atbat()
    foul_count = 0

    strikes = 0
    balls = 0
    pitches = []
    scoring_names = []
    first_pitch = True
    beaned = False
    third_out_triggered = False
    outcome = None

    if declared:
        team_name = team_a_name if is_top else team_b_name
        pitches.append(batter_status_message(batter, team_name))
        first_pitch = False

# --- Bunt Attempt: for batters with low power and if a runner is on third base ---
    if batter.power <= batter.chutzpah and base_runners[2] is not None and current_outs < 2:
        base_bunt_probability = max(0.02, batter.chutzpah * 0.05)
        adjusted_bunt_probability = base_bunt_probability + (base_runners[2].baserunning * 0.01)
        if random.random() < adjusted_bunt_probability:
            bunt_outcome = random.randint(1, 100) + batter.batting + batter.chutzpah
            # Determine which base is eligible for scoring; prioritize third.
            if base_runners[2] is not None:
                scoring_runner_index = 2
            elif base_runners[1] is not None:
                scoring_runner_index = 1
            else:
                scoring_runner_index = None

            # Bunt Hit: Batter bunts successfully.
            if bunt_outcome >= 86:
                # Instead of custom advancement, treat the outcome as a potential bunt.
                return "potential_bunt_hit", base_runners, pitches, current_outs, beaned, balls, strikes, []

            # Sacrifice Bunt: Batter bunts, is put out, but a runner (typically on third) scores.
            elif bunt_outcome >= 16:
                if scoring_runner_index is not None:
                    scored_runner = base_runners[scoring_runner_index]
                    base_runners[scoring_runner_index] = None
                else:
                    scored_runner = None
                # Advance remaining runners one base:
                # - Runner on first moves to second;
                # - Runner on second moves to third.
                new_bases = [None, None, None]
                if base_runners[0] is not None:
                    new_bases[1] = base_runners[0]
                if base_runners[1] is not None:
                    new_bases[2] = base_runners[1]
                # Batter is recorded as an out.
                current_outs += 1

                # Construct and append the bunt outcome message first.
                bso_display = format_bso(balls, strikes, current_outs)
                bunt_msg = f"{format_player_status(batter)} makes a sacrifice bunt play! {batter.name} is out, but "
                if scored_runner is not None:
                    bunt_msg += f"{scored_runner.name} scores! "
                else:
                    bunt_msg += "the runners advance! "
                bunt_msg += f"{display_bases_as_squares(new_bases)} {bso_display}"
                pitches.append(bunt_msg)

                # Now, if a runner scored, update score and log the riled down message.
                if scored_runner is not None:
                    if is_top:
                        score[team_a_name] += 1
                    else:
                        score[team_b_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_a_name if is_top else team_b_name)
                    if reduce_msg:
                        pitches.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        if is_top:
                            apply_riled_buff(team_a, bonus)
                        else:
                            apply_riled_buff(team_b, bonus)

                # Finally, append the current score update.
                score_line = f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                pitches.append(score_line)
                return "bunt_out", new_bases, pitches, current_outs, beaned, balls, strikes, []

            # Awry Bunt: The bunt goes awry, resulting in a double play.
            else:
                if scoring_runner_index is not None:
                    runner_name = base_runners[scoring_runner_index].name
                    base_runners[scoring_runner_index] = None
                else:
                    runner_name = "runner"
                current_outs += 2  # Both the batter and a runner are out.
                bso_display = format_bso(balls, strikes, current_outs)
                bunt_msg = (f"{format_player_status(batter)} attempts a bunt but it goes awry! Double play: both {batter.name} and "
                            f"{runner_name} are out. {display_bases_as_squares(base_runners)} {bso_display}")
                pitches.append(bunt_msg)
                return "bunt_dp", base_runners, pitches, current_outs, beaned, balls, strikes, []

    # --- Process pitch-by-pitch outcomes ---
    while strikes < 3 and balls < 4:
        if first_pitch and declared:
            team_name = team_a_name if is_top else team_b_name
            first_pitch = False

        bso_display = format_bso(balls, strikes, current_outs)
        batter_score = batter.batting
        pitcher_score = pitcher.pitching
        raw_roll = random.randint(1, 100)
        roll = raw_roll + (batter_score - pitcher_score)

        # Branch for the beaned walk triggered by raw_roll == 75.
        if raw_roll == 75:
            foul_mood.update(False)
            if random.random() < 0.20:
                beaned = True
                return "beaned_walk", base_runners, pitches, current_outs, beaned, balls, strikes, []
            else:
                balls += 1
                bso_display = format_bso(balls, strikes, current_outs)
                pitches.append(f"{format_player_status(batter)} - Ball {balls}! {bso_display}")
                if balls == 4:
                    return ("walk", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names)
                continue

        # Branch for the near-miss home run triggered by raw_roll == 100.
        if raw_roll == 100 and random.random() <= 0.1:
            foul_mood.update(False)
            bso_display = format_bso(balls, strikes, current_outs)
            event = "near_miss_hr"
            scoring_names = [r.name for r in base_runners if r is not None] + [batter.name]
            scoring = len(scoring_names)
            if is_top:
                score[team_a_name] += scoring
            else:
                score[team_b_name] += scoring
            new_bases = [None, None, None]
            score_update_msg = f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
            # Call reduce_on_score directly.
            if is_top:
                riled_message = riled_up.reduce_on_score(team_a_name)
            else:
                riled_message = riled_up.reduce_on_score(team_b_name)
            play_description, event = describe_full_play(
                batter,
                "near_miss_hr",
                [],
                "",
                new_bases,
                scoring_names,
                bso_display,
                score_update_msg,
                riled_message
            )
            pitches.append(play_description)
            return event, new_bases, pitches, current_outs, beaned, balls, strikes, scoring_names

        # Next, if roll is exactly 100 and the batter has at least 1 power, try the power HR second chance.
        if (roll == 100 and batter.power >= 1) or (roll == 99 and batter.power >= 6):
            if batter.power < 6:
                second_roll = random.randint(1, 5)
            else:
                second_roll = random.randint(6, 10)
            if second_roll <= batter.power:
                foul_mood.update(False)
                bso_display = format_bso(balls, strikes, current_outs)
                scoring_names = [r.name for r in base_runners if r is not None] + [batter.name]
                scoring = len(scoring_names)
                if is_top:
                    score[team_a_name] += scoring
                else:
                    score[team_b_name] += scoring
                new_bases = [None, None, None]
                # Call reduce_on_score to get the riled-down message.
                if is_top:
                    riled_message = riled_up.reduce_on_score(team_a_name)
                else:
                    riled_message = riled_up.reduce_on_score(team_b_name)
                score_update_msg = f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
                play_description, event = describe_full_play(
                    batter,
                    "home run",
                    [],
                    "",
                    new_bases,
                    scoring_names,
                    bso_display,
                    score_update_msg,
                    riled_message
                )
                pitches.append(play_description)
                event = "home run"
                return event, new_bases, pitches, current_outs, beaned, balls, strikes, scoring_names
            # If the power HR chance fails, fall through to the normal hit branch.

        # Finally, process a regular home run for rolls of 102 or higher.
        if roll >= 101:
            foul_mood.update(False)
            bso_display = format_bso(balls, strikes, current_outs)
            scoring_names = [r.name for r in base_runners if r is not None] + [batter.name]
            scoring = len(scoring_names)
            if is_top:
                score[team_a_name] += scoring
            else:
                score[team_b_name] += scoring
            new_bases = [None, None, None]
            # Call reduce_on_score to get the riled-down message.
            if is_top:
                riled_message = riled_up.reduce_on_score(team_a_name)
            else:
                riled_message = riled_up.reduce_on_score(team_b_name)
            score_update_msg = f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}"
            play_description, event = describe_full_play(
                batter,
                "home run",
                [],
                "",  # batter movement message
                new_bases,
                scoring_names,
                bso_display,
                score_update_msg,
                riled_message
            )
            pitches.append(play_description)
            event = "home run"
            return event, new_bases, pitches, current_outs, beaned, balls, strikes, scoring_names

        # Result: Ball is Hit
        # Calculate the effective threshold based on batter's agility.
        # For agility 0, threshold is 80.
        # For agility 1-2, threshold is 79; 3-4 → 78; 5-6 → 77; 7-8 → 76; 9-10 → 75.
        elif batter.agility == 0:
            effective_threshold = 80
        else:
            effective_threshold = max(75, 80 - ((batter.agility + 1) // 2))
        # Initialize a flag for whether the hit attempt succeeds.
        hit_attempt_success = False
        # Attempt the hit if the roll is at least the effective threshold.
        if roll >= effective_threshold:
            # If the roll is exactly equal to the threshold and the batter is at the lower end of the tier
            # (i.e. an odd agility value), apply a 50% chance for success.
            if roll == effective_threshold and batter.agility > 0 and (batter.agility % 2 == 1):
                if random.random() < 0.5:
                    hit_attempt_success = False  # Fail the hit attempt.
                else:
                    hit_attempt_success = True
            else:
                hit_attempt_success = True
        # If the hit attempt succeeds, update the foul mood and determine the hit type.
        if hit_attempt_success:
            foul_mood.update(False)
            hit_roll = random.randint(1, 100)
            if hit_roll >= 99:
                return "potential_triple", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names
            elif hit_roll >= 80:
                return "potential_double", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names
            else:
                return "potential_single", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names


        elif 45 <= roll < effective_threshold:
            foul_ball_threshold = 56  # Adjust this value to change foul ball frequency.
            if roll < foul_ball_threshold:
                foul_count += 1
                if foul_count >= 6:
                    bso_display = format_bso(balls, strikes, current_outs)
                    pitches.append(f"{format_player_status(batter)} - Foul Ball! {bso_display}")
                    bso_display = format_bso(balls, strikes, current_outs)
                    pitches.append(
                        f"⚡ THE GODS ARE FED UP WITH {format_player_status(batter)}'s FOULS! {format_player_status(batter)} is SMITED! ⚡")
                    batter.pending_death = True
                    return "foul_limit_out", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names
                else:
                    if strikes < 2:
                        strikes += 1
                    bso_display = format_bso(balls, strikes, current_outs)
                    pitches.append(f"{format_player_status(batter)} - Foul Ball! {bso_display}")
                    bonus_increased = foul_mood.update(True)
                    if bonus_increased:
                        bonus_message = foul_mood.get_bonus_message()
                        pitches.append(f"The players are getting tired of this... {bonus_message}")
            else:
                balls += 1
                bso_display = format_bso(balls, strikes, current_outs)
                pitches.append(f"{format_player_status(batter)} - Ball {balls}! {bso_display}")
                if balls == 4:
                    return ("walk", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names)
            continue

        if batter.chutzpah == 0:
            strike_threshold = 20
            flyout_threshold = 10
        else:
            strike_threshold = 20 - ((batter.chutzpah + 1) // 2)
            flyout_threshold = 10 - ((batter.chutzpah + 1) // 2)
        strike_attempt = False
        if roll >= strike_threshold:
            if roll == strike_threshold and batter.chutzpah > 0 and (batter.chutzpah % 2 == 1):
                chance = random.random()
                if chance >= 0.5:
                    strike_attempt = True
            else:
                strike_attempt = True
        if strike_attempt:
            foul_mood.update(False)
            if strikes == 2:
                current_outs += 1
                bso_display = format_bso(balls, strikes, current_outs)
                if roll == 44:
                    pitches.append(
                        f"{format_player_status(batter)} takes a swing... The ump calls Strike 3! "
                        f"But the offense may dispute the call... with violence. {bso_display}"
                    )
                else:
                    strike_type = random.choice(["swinging", "looking"])
                    pitches.append(
                        f"{format_player_status(batter)} - Strike 3! {batter.name} strikes out, {strike_type}. {bso_display}"
                    )
                event = "close_call_out" if roll == 44 else "strike_out"
                return event, base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names
            else:
                strikes += 1
                bso_display = format_bso(balls, strikes, current_outs)
                pitches.append(f"{format_player_status(batter)} - Strike {strikes}! {bso_display}")
        else:
            flyout_attempt = False
            if roll >= flyout_threshold:
                if roll == flyout_threshold and batter.chutzpah > 0 and (batter.chutzpah % 2 == 1):
                    chance = random.random()
                    if chance >= 0.5:
                        flyout_attempt = True
                else:
                    flyout_attempt = True
            if flyout_attempt:
                foul_mood.update(False)
                current_outs += 1
                bso_display = format_bso(balls, strikes, current_outs)
                out_description = random.choice([
                    "sends the ball a bit too high... Flyout!",
                    "pops it up and the ball is caught infield. Popout!",
                    "lines it sharply for a Line Out!"
                ])
                pitches.append(f"{format_player_status(batter)} {out_description} {bso_display}")
                return "fly out", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names
            foul_mood.update(False)
            current_outs += 1
            bso_display = format_bso(balls, strikes, current_outs)
            combined_msg = f"{format_player_status(batter)} - Ground Out! {bso_display}"
            base_tag_chance = 0.20
            extra_bonus = 0
            shortstop = defensive_positions.get("shortstop")
            if shortstop is not None and is_active(shortstop):
                extra_bonus = shortstop.fielding * 0.02
                shortstop_name = shortstop.name
            else:
                shortstop_name = "the shortstop"
            extra_tag_chance = base_tag_chance + extra_bonus
            shortstop_called = False
            for base_idx, runner in enumerate(base_runners):
                if runner is not None:
                    if random.random() < extra_tag_chance:
                        base_text = base_number_to_text(base_idx)
                        if not shortstop_called:
                            current_outs += 1
                            bso_display = format_bso(balls, strikes, current_outs)
                            tag_msg = f" {format_player_status(runner)} is caught in a rundown and tagged out by {shortstop_name} at {base_text}! {bso_display}"
                            shortstop_called = True
                        else:
                            current_outs += 1
                            bso_display = format_bso(balls, strikes, current_outs)
                            tag_msg = f" {format_player_status(runner)} is tagged out at {base_text}! {bso_display}"
                        combined_msg += tag_msg
                        base_runners[base_idx] = None
            pitches.append(combined_msg)
            return "ground out", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names

    print("Warning: at_bat_with_pitch_sequence reached the end without returning a result!")
    print(f"batter: {batter.name}, balls: {balls}, strikes: {strikes}, outs: {current_outs}")
    return "error", base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names

# === Brawl System === #
# Base chances (in percentages) for various brawl-triggering events.
BRAWL_BASE_CHANCES = {
    **dict.fromkeys(["beaned", "collision"], 50),
    **dict.fromkeys(["near_miss_hr", "grand_slam"], 25),
    **dict.fromkeys(["close_tag_out", "close_call_out"], 25),
    **dict.fromkeys(["single", "double", "triple", "strike_out", "fly out", "ground out"], -50)
}

def maybe_trigger_brawl(event_type, team_a, team_b, team_a_name, team_b_name, log, foul_mood):
    if event_type in BRAWL_BASE_CHANCES:
        base_chance = BRAWL_BASE_CHANCES[event_type]
        bonus = foul_mood.bonus if hasattr(foul_mood, "bonus") else 0
        chance = max(0, min(100, base_chance + bonus))
        roll = random.randint(1, 100)
        if roll <= chance:
            brawl_log = simulate_brawl(team_a, team_b, team_a_name, team_b_name)
            log.extend(brawl_log)
            finalize_pending_deaths(team_a)
            finalize_pending_deaths(team_b)
            foul_mood.reset()

def simulate_brawl(team_a, team_b, team_a_name, team_b_name):
    log = []
    log.append("💪 A BRAWL HAS ERUPTED ON THE FIELD! 💪")
    team_a_brawlers = simulate_brawl_team(team_a)
    team_b_brawlers = simulate_brawl_team(team_b)
    random.shuffle(team_a_brawlers)
    random.shuffle(team_b_brawlers)
    team_a_total = sum(b['score'] for b in team_a_brawlers) + random.randint(1, 100)
    team_b_total = sum(b['score'] for b in team_b_brawlers) + random.randint(1, 100)
    log.append(f"{team_a_name} ({team_a_total}) vs {team_b_name} ({team_b_total})")
    if team_a_total > team_b_total:
        margin = team_a_total - team_b_total
        casualties_team_b = max(1, int(calculate_num_injuries(margin) * (team_a_total / team_b_total) * 0.5))
        casualties_team_a = max(1, int(calculate_num_injuries(margin) * (team_b_total / team_a_total) * 0.5))
    elif team_b_total > team_a_total:
        margin = team_b_total - team_a_total
        casualties_team_a = max(1, int(calculate_num_injuries(margin) * (team_b_total / team_a_total) * 0.5))
        casualties_team_b = max(1, int(calculate_num_injuries(margin) * (team_a_total / team_b_total) * 0.5))
    else:
        casualties_team_a = casualties_team_b = 1

    team_a_casualties = []
    for i in range(casualties_team_a):
        if i >= len(team_a_brawlers):
            break
        roll = random.randint(1, 100)
        outcome = resolve_injury(roll)
        if team_a_total > team_b_total and outcome in ["Knocked Out", "Killed"]:
            outcome = "Injured"
        player = team_a_brawlers[i]['player']
        team_a_casualties.append((player, outcome))
        apply_injury_to_player(player, outcome, team_a)

    team_b_casualties = []
    for i in range(casualties_team_b):
        if i >= len(team_b_brawlers):
            break
        roll = random.randint(1, 100)
        outcome = resolve_injury(roll)
        if team_b_total > team_a_total and outcome in ["Knocked Out", "Killed"]:
            outcome = "Injured"
        player = team_b_brawlers[i]['player']
        team_b_casualties.append((player, outcome))
        apply_injury_to_player(player, outcome, team_b)

    severity_order = {
        "winded": 1,
        "shook up": 2,
        "injured": 3,
        "knocked out": 4,
        "killed": 5
    }

    def group_casualties(casualties):
        groups = {}
        for player, outcome in casualties:
            if outcome.startswith("Winded"):
                key = "winded"
            elif outcome.startswith("Shook Up"):
                key = "shook up"
            elif outcome.startswith("Injured"):
                key = "injured"
            elif outcome.startswith("Knocked Out"):
                key = "knocked out"
            elif outcome.startswith("Killed"):
                key = "killed"
            else:
                key = outcome.lower()
            groups.setdefault(key, []).append(player.name)
        return groups

    team_a_groups = group_casualties(team_a_casualties)
    team_b_groups = group_casualties(team_b_casualties)

    def build_casualty_message(team_name, groups):
        if not groups:
            return ""
        messages = []
        sorted_groups = sorted(groups.items(), key=lambda item: severity_order.get(item[0], 100))
        for injury_type, names in sorted_groups:
            if len(names) == 1:
                messages.append(f"{names[0]} is {injury_type}")
            else:
                if len(names) == 2:
                    names_str = " and ".join(names)
                else:
                    names_str = ", ".join(names[:-1]) + " and " + names[-1]
                messages.append(f"{names_str} are {injury_type}")
        return f"{team_name} casualties: " + " ".join(msg + "!" for msg in messages)

    team_a_message = build_casualty_message(team_a_name, team_a_groups)
    team_b_message = build_casualty_message(team_b_name, team_b_groups)

    if team_a_message:
        log.append(team_a_message)
    if team_b_message:
        log.append(team_b_message)

    log.append("🌞 Order is restored and the game continues! 🌞")
    return log

def simulate_brawl_team(team):
    results = []
    for player in team:
        if is_active(player):
            score_val = player.brawling
            results.append({"player": player, "score": score_val})
    return results

def calculate_num_injuries(score_diff):
    injuries = (score_diff // 10)
    return min(9, injuries)

def resolve_injury(roll):
    if roll <= 30:
        return "Winded"
    elif roll <= 55:
        return "Shook Up"
    elif roll <= 75:
        return "Injured"
    elif roll <= 95:
        return "Knocked Out"
    else:
        return "Killed"

def apply_injury_to_player(player, outcome, team):
    if getattr(player, "is_dead", False):
        return
    if hasattr(player, "knockout_halves_remaining") and player.knockout_halves_remaining > 0:
        return

    if outcome.startswith("Killed"):
        player.pending_death = True
        return
    elif outcome.startswith("Knocked Out") or outcome.startswith("Collision"):
        player.knockout_halves_remaining = 5
        return

    # Determine reduction and corresponding new injury status.
    if outcome.startswith("Winded"):
        reduction = 2
        new_status = "Winded"
    elif outcome.startswith("Shook Up"):
        reduction = 4
        new_status = "Shook Up"
    elif outcome.startswith("Injured"):
        reduction = 8
        new_status = "Injured"
    else:
        reduction = 0
        new_status = None

    # Instead of permanently subtracting from the current stats, we record the debuff.
    player.injury_debuff = reduction
    player.injury_status = new_status
    update_player_stats(player)

# Recovery #
def calculate_recovery_chance(player):
    return max(0.1, player.power / 5)

def update_injury_status(team, team_name, recovery_messages):
    # Define the order of injury tiers and the associated reduction values.
    tier_order = ["Knocked Out", "Injured", "Shook Up", "Winded"]
    injury_reductions = {
         "Winded": 2,
         "Shook Up": 4,
         "Injured": 8,
         "Knocked Out": None  # Special handling for knocked out players.
    }

    for player in team:
        if not hasattr(player, "recovery_bonus"):
            player.recovery_bonus = 0.0

        # Determine the current tier.
        current_tier = None
        if hasattr(player, "knockout_halves_remaining") and player.knockout_halves_remaining > 0:
            current_tier = "Knocked Out"
        elif player.injury_status:
            current_tier = player.injury_status

        if current_tier is not None:
            base_chance = calculate_recovery_chance(player)
            effective_chance = min(1.0, base_chance + player.recovery_bonus)
            # Full recovery: 5% chance on a 1d100 roll
            if random.randint(1, 100) <= 5:
                player.injury_status = None
                player.injury_debuff = 0
                update_player_stats(player)
                if hasattr(player, "knockout_halves_remaining"):
                    delattr(player, "knockout_halves_remaining")
                recovery_messages.append(
                    f"💖 {player.name} makes an extraordinary recovery and is fully healed!"
                )
                player.recovery_bonus = 0.0
            else:
                # Attempt partial recovery using an effective roll (0-1)
                effective_roll = random.uniform(0, 1)
                if effective_roll < effective_chance:
                    if current_tier in tier_order:
                        current_index = tier_order.index(current_tier)
                        new_status = tier_order[current_index + 1] if current_index < len(tier_order) - 1 else None
                    else:
                        new_status = None
                    old_status = current_tier
                    player.injury_status = new_status
                    if current_tier == "Knocked Out" and hasattr(player, "knockout_halves_remaining"):
                        delattr(player, "knockout_halves_remaining")
                    if new_status is None:
                        player.injury_debuff = 0
                        update_player_stats(player)
                        recovery_messages.append(f"💖 {player.name} has fully recovered from {old_status}!")
                    else:
                        player.injury_debuff = injury_reductions[new_status]
                        update_player_stats(player)
                        recovery_messages.append(f"{player.name} recovers from {old_status} to {new_status}!")
                    player.recovery_bonus = 0.0
                else:
                    player.recovery_bonus += 0.1

#===== Outcome Descriptions =====#
def get_hit_description(hit_type, batter_name):
    """
    Returns a randomized description string based on the hit type.
    """
    single_descriptions = [
        f"{batter_name} punches a single through the infield,",
        f"{batter_name} rolls a single past the diving infielder,",
        f"{batter_name} slaps a sharp single into shallow center,",
        f"{batter_name} muscles a single into right field,",
        f"{batter_name} bloops a single just over the shortstop,",
        f"{batter_name} drops a single into no-man's land,",
        f"{batter_name} rips a single up the middle,",
        f"{batter_name} pokes a single the other way,",
        f"{batter_name} smacks a hard single into left field,",
        f"{batter_name} bounces a single through the infield,"
    ]
    double_descriptions = [
        f"{batter_name} sends it flying down the line for a double,",
        f"{batter_name} smacks a double into the gap,",
        f"{batter_name} hits a ground-rule double,",
        f"{batter_name} rips a double off the outfield wall,",
        f"{batter_name} drives a double,"
    ]
    triple_descriptions = [
        f"{batter_name} laces a triple into the corner,",
        f"{batter_name} crushes a triple deep into the outfield,",
        f"{batter_name} legs out a triple,",
        f"{batter_name} finds the gap for a triple,",
        f"{batter_name} smokes a triple,"
    ]
    bunt_descriptions = [
        f"{batter_name} tips a surprise bunt, sending the ball deep into the gap,",
        f"{batter_name} executes a surprise bunt with finesse,",
        f"{batter_name} surprisingly bunts the ball infield, hoping for advancement,"
    ]

    if hit_type == "single":
        return random.choice(single_descriptions)
    elif hit_type == "double":
        return random.choice(double_descriptions)
    elif hit_type == "triple":
        return random.choice(triple_descriptions)
    elif hit_type == "bunt_hit":
        return random.choice(bunt_descriptions)
    # For home runs, the description is handled separately.
    raise ValueError(f"Unhandled hit type: {hit_type}")

def format_scorers(scorers):
    """
    Given a list of scorer names, formats them into a human-readable string.
    """
    if not scorers:
        return ""
    elif len(scorers) == 1:
        return scorers[0]
    elif len(scorers) == 2:
        return " and ".join(scorers)
    else:
        # For three or more, comma-separate and join the last two with 'and'
        return ", ".join(scorers[:-1]) + ", and " + scorers[-1]

def describe_full_play(batter, hit_type, runner_movements, batter_movement, base_runners,
                         runners_scoring=[], final_bso="", score_update="", riled_message=""):
    """
    Build a complete play-by-play description for a hit.

    For home runs and near-miss HRs, the output will be built as:
      1. The basic home run description (or grand slam if 4 scorers)
      2. The riled-down message (if provided)
      3. The current score update

    For other hit types, we use a generic description.
    """
    # Create a visual representation of the bases using your helper.
    base_state = display_bases_as_squares(base_runners) if base_runners is not None else ""

    if hit_type not in ["home run", "near_miss_hr"]:
        # For non-home run events, use the generic hit description.
        generic_description = get_hit_description(hit_type, batter.name)
        if batter_movement:
            description = f"{generic_description} {batter_movement}."
        else:
            description = f"{generic_description}."
        if runner_movements:
            description += " " + " ".join(runner_movements)
        if final_bso:
            description += " " + final_bso
        # Append the current bases state.
        if base_state:
            description += " " + base_state
        if score_update:
            description += "\n" + score_update
        return description, hit_type
    else:
        # Handle home run and near-miss HR events.
        formatted_scorers = format_scorers(runners_scoring)
        verb = "scores" if len(runners_scoring) == 1 else "score"
        if len(runners_scoring) == 4:
            # Grand slam case
            event = "grand_slam"
            if hit_type == "near_miss_hr":
                base_desc = (f"💥 {format_player_status(batter)} - It's a hit... THE BALL BARELY CLEARS THE FENCE! "
                             f"GRAND SLAM! 💥 {formatted_scorers} {verb}!")
            else:
                base_desc = (f"💥 {format_player_status(batter)} SENDS IT INTO ORBIT! GRAND SLAM! 💥 {formatted_scorers} {verb}!")
        else:
            event = hit_type
            if hit_type == "near_miss_hr":
                base_desc = (f"{format_player_status(batter)} - It's a hit... THE BALL BARELY CLEARS THE FENCE! "
                             f"HOME RUN! {formatted_scorers} {verb}!")
            else:
                base_desc = (f"{format_player_status(batter)} SMASHES A HOME RUN OUT OF THE PARK! "
                             f"{formatted_scorers} {verb}!")
        # Append runner and batter movements if provided.
        if runner_movements:
            base_desc += " " + " ".join(runner_movements)
        if batter_movement:
            base_desc += " " + batter_movement
        if final_bso:
            base_desc += " " + final_bso
        # Append the current bases state.
        if base_state:
            base_desc += " " + base_state
        if riled_message:
            base_desc += "\n" + riled_message
        if score_update:
            base_desc += "\n" + score_update
        return base_desc, event

#====== Half Innings ======#
def half_inning_with_fixed_base_running(
    team_name,
    batting_order,
    pitcher,
    base_runners,
    current_batter_index,
    inning,
    is_top,
    team_a_name,
    team_b_name,
    defensive_positions,
    score,
    team_a,
    team_b,
    riled_up,
    foul_mood=None,
    suppress_riled=False
):
    play_by_play_log = []
    # Reset bases at the start of the half–inning.
    base_runners = [None, None, None]
    balls = 0
    strikes = 0
    outs = 0
    inning_score = 0
    bso_display = format_bso(balls, strikes, outs)
    # Update injury statuses and capture recovery messages.
    recovery_messages = []
    update_injury_status(team_a, team_a_name, recovery_messages)
    update_injury_status(team_b, team_b_name, recovery_messages)
    play_by_play_log.extend(recovery_messages)
    # Ensure we have a FoulMood instance.
    if foul_mood is None:
        foul_mood = FoulMood()
    # Decrement knockout timers for players on both teams.
    for player in team_a:
        if hasattr(player, 'knockout_halves_remaining') and player.knockout_halves_remaining > 0:
            player.knockout_halves_remaining -= 1
    for player in team_b:
        if hasattr(player, 'knockout_halves_remaining') and player.knockout_halves_remaining > 0:
            player.knockout_halves_remaining -= 1
    # Auto-forfeit: if there are no batters left, forfeit immediately.
    if len(batting_order) == 0:
        play_by_play_log = [f"{team_name} has no players left and must forfeit immediately!"]
        return 0, current_batter_index, play_by_play_log, True
    # Define half_team for logging.
    half_team = team_a_name if is_top else team_b_name

    while True:
        # Forfeit if no active batters remain.
        if not any(is_active(b) for b in batting_order):
            play_by_play_log.append(f"{team_name} has no active players left and must forfeit immediately!")
            return inning_score, current_batter_index, play_by_play_log, True

        batter = batting_order[current_batter_index % len(batting_order)]
        status_msg = batter_status_message(batter, team_name)
        if status_msg is not None:
            play_by_play_log.append(status_msg)

        if getattr(batter, "pending_death", False):
            batter.is_dead = True
            batter.pending_death = False

        # Skip the at–bat if the batter is inactive.
        if not is_active(batter):
            current_batter_index += 1
            continue

        base_runners, score, outs, end_at_bat = process_pickoff_attempts(
            base_runners,
            pitcher,
            play_by_play_log,
            score,
            is_top,
            team_a_name,
            team_b_name,
            defensive_positions,
            balls,
            strikes,
            outs,
            riled_up,
            team_a,
            team_b
        )
        if end_at_bat:
            # End the at-bat immediately.
            play_by_play_log.append(f"{batter.name} mopes out of the batter's box, disappointed. 😞")
            break

        #==== stealing ====#
        def attempt_steal(runner, defensive_positions):
            """
            Determines whether a runner can successfully steal a base.
            Returns a tuple with the result ("steal_success", "caught", or "no_defense")
            and the corresponding roll value.
            """
            catcher = defensive_positions.get("catcher")
            if not catcher:
                return "no_defense", 0
            runner_score = max(runner.baserunning, runner.chutzpah)
            # Use calculate_fielder_score so that an inactive catcher contributes 0
            catcher_score = calculate_fielder_score(catcher)
            steal_roll = random.randint(1, 100) + (runner_score - catcher_score)
            if steal_roll >= 40:
                return "steal_success", steal_roll
            else:
                return "caught", steal_roll

        # --- At-Bat Delay Steal Attempt ---
        for base_index in [2, 1, 0]:
            if base_runners[base_index] is not None and is_active(base_runners[base_index]):
                if base_index < 2 and base_runners[base_index + 1] is not None:
                    continue
                runner = base_runners[base_index]
                multiplier = {0: 1.0, 1: 0.6, 2: 0.2}[base_index]
                steal_probability = max((runner.chutzpah / 5) * 0.275 * multiplier, 0.01)
                if random.random() < steal_probability:
                    result, steal_roll = attempt_steal(runner, defensive_positions)
                    if result == "steal_success":
                        if base_index == 2:
                            base_runners[2] = None
                            if is_top:
                                score[team_a_name] += 1
                            else:
                                score[team_b_name] += 1
                            play_by_play_log.append(
                                f"{format_player_status(runner)} steals home base and scores! {display_bases_as_squares(base_runners)}")
                            if is_top:
                                reduce_msg = riled_up.reduce_on_score(team_a_name)
                                if reduce_msg:
                                    play_by_play_log.append(reduce_msg)
                                    bonus = riled_up.get_bonus()
                                    apply_riled_buff(team_a, bonus)
                            else:
                                reduce_msg = riled_up.reduce_on_score(team_b_name)
                                if reduce_msg:
                                    play_by_play_log.append(reduce_msg)
                                    bonus = riled_up.get_bonus()
                                    apply_riled_buff(team_b, bonus)
                            play_by_play_log.append(f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}")
                        else:
                            next_base_text = base_number_to_text(base_index + 1)
                            base_runners[base_index + 1] = runner
                            base_runners[base_index] = None
                            play_by_play_log.append(
                                f"{format_player_status(runner)} attempts to steal {next_base_text} and is safe! {display_bases_as_squares(base_runners)}"
                            )
                    elif result == "caught":
                        next_base_text = base_number_to_text(base_index + 1)
                        base_runners[base_index] = None
                        outs += 1
                        updated_bso = format_bso(balls, strikes, outs)
                        play_by_play_log.append(
                            f"{format_player_status(runner)} attempts to steal {next_base_text} and is caught backtracking! Out! "
                            f"{updated_bso} {display_bases_as_squares(base_runners)}"
                        )
                        if outs >= 3:
                            break
        # --- End Delayed Steal Attempt ---
        if outs >= 3:
            end_at_bat = True

        if end_at_bat:
            # End the at-bat immediately.
            play_by_play_log.append(f"{batter.name} squints disapprovingly at {format_player_status(runner)} and exits the batter's box, annoyed. 😒")
            break

        old_total = score[team_a_name] if is_top else score[team_b_name]

        # --- At–Bat Outcome ---
        while True:
            at_bat_result, updated_base_runners, pitches, current_outs, beaned, balls, strikes, scoring_names = at_bat_with_pitch_sequence(
                batter,
                pitcher,
                base_runners,
                outs,
                defensive_positions,
                is_top,
                team_a_name,
                team_b_name,
                score,
                team_a,
                team_b,
                riled_up,
                declared=False,
                foul_mood=foul_mood
            )
            play_by_play_log.extend(pitches)
            outs = current_outs
            base_runners = updated_base_runners
            base_runners = remove_dead_from_bases(base_runners)

            # Only break if a decisive outcome is reached.
            if at_bat_result in ["potential_single", "potential_double", "potential_triple", "walk",
                                 "beaned_walk", "potential_bunt_hit", "bunt_out", "bunt_dp", "strike_out",
                                 "fly out", "ground out", "home run", "grand_slam", "near_miss_hr", "close_call_out", "foul_limit_out"]:
                break
            # Otherwise, the at–bat continues (i.e. more pitches for the same batter).

        old_total = score[team_a_name] if is_top else score[team_b_name]
        # Compute a BSO display to pass into baserunning.
        final_bso = format_bso(0, 0, outs)

        if at_bat_result.startswith("potential_"):
            # Outcome is a hit. Process it to update bases and generate hit descriptions.
            (updated_bases,
            scoring_runners,
            runner_movements,
            batter_movement,
            play_by_play_message_hit,
            runners_scoring,
            updated_outs
             ) = process_hit_with_correct_base_running(
                batter,
                at_bat_result,
                base_runners,
                is_top,
                team_a_name,
                team_b_name,
                defensive_positions,
                score,
                team_a,
                team_b,
                foul_mood,
                riled_up,
                final_bso,
                outs
            )
            outs = updated_outs
            inning_score += scoring_runners
            base_runners = updated_bases
            play_by_play_log.extend(play_by_play_message_hit)
        elif at_bat_result in ["walk", "beaned_walk"]:
            # These outcomes are handled by the walk block later.
            pass
        else:
            # Outcome is an out (fly out, ground out, or strikeout) – no hit to process.
            # (You might log an additional message here if desired.)
            pass

        new_total = score[team_a_name] if is_top else score[team_b_name]
        inning_score += (new_total - old_total)
        balls = 0
        strikes = 0

        # --- Handle Walks ---
        if at_bat_result in ["walk", "beaned_walk"]:
            loaded_walk = (base_runners[0] is not None and base_runners[1] is not None and base_runners[2] is not None)
            if loaded_walk:
                forced_runner = base_runners[2]
                # First, build and log the walk action message:
                new_first = batter
                new_second = base_runners[0]
                new_third = base_runners[1]
                base_runners = [new_first, new_second, new_third]
                walk_msg = (f"{format_player_status(batter)} takes a walk and advances to first. "
                            f"{forced_runner.name} advances to home plate on the walk! {display_bases_as_squares(base_runners)}")
                play_by_play_log.append(walk_msg)
                # Next, update score and then log the riled down message:
                if is_top:
                    score[team_a_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_a_name)
                    if reduce_msg:
                        play_by_play_log.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_a, bonus)
                else:
                    score[team_b_name] += 1
                    reduce_msg = riled_up.reduce_on_score(team_b_name)
                    if reduce_msg:
                        play_by_play_log.append(reduce_msg)
                        bonus = riled_up.get_bonus()
                        apply_riled_buff(team_b, bonus)
                # Finally, log the current score update.
                play_by_play_log.append(f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}")
            else:
                if base_runners[0] is not None:
                    if base_runners[1] is None:
                        base_runners[1] = base_runners[0]
                    else:
                        base_runners[2] = base_runners[1]
                        base_runners[1] = base_runners[0]
                    base_runners[0] = batter
                else:
                    base_runners[0] = batter
                if at_bat_result == "beaned_walk":
                    play_by_play_log.append(f"{format_player_status(batter)} is beaned by {pitcher.name}! "
                                            f"Automatic walk! {batter.name} advances to first. "
                                            f"The offense is brooding... {display_bases_as_squares(base_runners)}")
                    maybe_trigger_brawl("beaned", team_a, team_b, team_a_name, team_b_name, play_by_play_log, foul_mood)
                else:
                    walk_msg = f"{format_player_status(batter)} takes a walk and advances to first."
                    play_by_play_log.append(f"{walk_msg} {display_bases_as_squares(base_runners)}")

        # Check if a brawl needs to be triggered.
        if at_bat_result in ["beaned_walk", "near_miss_hr", "grand_slam", "close_call_out",
                             "single", "double", "triple", "strike_out", "fly out", "ground out"]:
            maybe_trigger_brawl(at_bat_result, team_a, team_b, team_a_name, team_b_name, play_by_play_log, foul_mood)

        #next batter
        current_batter_index += 1

        if outs >= 3:
            if outs == 4:
                play_by_play_log.append("The offense is insulted by the defense's unnecessary 4th out! 🤡")
            elif outs == 5:
                play_by_play_log.append("The offense is greatly insulted by the defense's unnecessary 4th and 5th outs! 👺")
            elif outs == 6:
                play_by_play_log.append("The offense is extremely insulted by the defense's unnecessary 4th, 5th, and 6th outs! 💩💩💩")
            break

    # Riled Up check on the score deficit.
    if not suppress_riled:  # Only do this if we're not suppressing riled messages
        if is_top:
            offense_score = score[team_a_name]
            defense_score = score[team_b_name]
        else:
            offense_score = score[team_b_name]
            defense_score = score[team_a_name]

        deficit = defense_score - offense_score
        if deficit >= 3 and riled_up is not None:
            deficit_msg = riled_up.trigger_by_deficit(deficit, team_name)
            if deficit_msg:
                bonus = riled_up.get_bonus()
                batting_team = team_a if is_top else team_b
                apply_riled_buff(batting_team, bonus)
                play_by_play_log.append(deficit_msg)

    summary_lines = []
    summary_lines.append("")
    summary_lines.append(f"END OF THE {'TOP' if is_top else 'BOTTOM'} OF INNING {inning}. "
                         f"📊 Current Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}")
    summary_lines.append("")
    play_by_play_log.extend(summary_lines)

# Finalize pending deaths for both teams.
    finalize_pending_deaths(team_a)
    finalize_pending_deaths(team_b)

    return inning_score, current_batter_index, play_by_play_log, False

#==== Full Game Compiler ====
def play_full_game(team_a_master, team_b_master, pitchers_a, pitchers_b, team_a_name, team_b_name):
    team_a = copy.deepcopy(team_a_master)
    team_b = copy.deepcopy(team_b_master)
    # Use a mutable score dictionary.
    score = {team_a_name: 0, team_b_name: 0}
    full_play_by_play = []
    full_play_by_play.append("🚩️ **Welcome to today's game!** 🚩️")
    full_play_by_play.append(f"🏆 **Matchup: {team_a_name} vs. {team_b_name}** 🏆")
    full_play_by_play.append("💥 **PLAY BALL!** 💥\n")

    # Create a single persistent FoulMood instance for the entire game.
    foul_mood = FoulMood()

    # Create a RiledUp instance for each team.
    riled_up_a = RiledUp()
    riled_up_b = RiledUp()

    # Set up batting orders and pointers.
    batting_order_a = team_a.copy()  # contains player objects directly
    batting_order_b = team_b.copy()
    current_batter_a = 0
    current_batter_b = 0

    # Set up pitcher orders and pointers.
    current_pitcher_a_index = 0
    current_pitcher_b_index = 0

    # Process the standard 9 innings.
    for inning in range(1, 10):
        # --- Select pitcher for Team B with fallback ---
        try:
            pitcher_b = select_pitcher(team_b)
        except (IndexError, ValueError):
            pitcher_b = random.choice(team_b) if team_b else None
        if pitcher_b not in team_b:
            pitcher_b = random.choice(team_b) if team_b else None
        current_pitcher_b_index += 1

        # --- Select pitcher for Team A with fallback ---
        try:
            pitcher_a = select_pitcher(team_a)
        except (IndexError, ValueError):
            pitcher_a = random.choice(team_a) if team_a else None
        if pitcher_a not in team_a:
            pitcher_a = random.choice(team_a) if team_a else None
        current_pitcher_a_index += 1

        # Assign defensive positions.
        defensive_positions_b = assign_defensive_positions([p for p in team_b if p != pitcher_b])
        defensive_positions_b["pitcher"] = pitcher_b
        defensive_positions_a = assign_defensive_positions([p for p in team_a if p != pitcher_a])
        defensive_positions_a["pitcher"] = pitcher_a

        # --- Top of the Inning ---
        full_play_by_play.append(f"=== Inning {inning}, Top: {team_a_name} Batting ===")
        full_play_by_play.append(f"⚾ Pitching for {team_b_name}: {pitcher_b.name} ⚾")
        inning_score_a, current_batter_a, play_by_play_a, forfeit_a = \
            half_inning_with_fixed_base_running(
                team_a_name, team_a, pitcher_b, [], current_batter_a, inning, True,
                team_a_name, team_b_name, defensive_positions_b, score, team_a, team_b,
                foul_mood=foul_mood, riled_up=riled_up_a
            )
        full_play_by_play.extend(play_by_play_a)
        if forfeit_a:
            full_play_by_play.append(f"{team_a_name} has forfeited! {team_b_name} is declared the winner.")
            return full_play_by_play

        # --- Bottom of the Inning ---
        full_play_by_play.append(f"=== Inning {inning}, Bottom: {team_b_name} Batting ===")
        full_play_by_play.append(f"⚾ Pitching for {team_a_name}: {pitcher_a.name} ⚾")
        bottom_suppress = True if inning == 9 else False
        inning_score_b, current_batter_b, play_by_play_b, forfeit_b = \
            half_inning_with_fixed_base_running(
                team_b_name, team_b, pitcher_a, [], current_batter_b, inning, False,
                team_a_name, team_b_name, defensive_positions_a, score, team_a, team_b,
                foul_mood=foul_mood, riled_up=riled_up_b, suppress_riled=bottom_suppress
            )
        full_play_by_play.extend(play_by_play_b)
        if forfeit_b:
            full_play_by_play.append(f"{team_b_name} has forfeited! {team_a_name} is declared the winner.")
            return full_play_by_play

    # --- Extra Innings (if tied after 9 innings) ---
    if score[team_a_name] == score[team_b_name]:
        full_play_by_play.append("✨ Game tied at the end of the 9th inning. Extra innings begin! ✨\n")
        inning = 10
        extra_pitcher_order_top = list(range(len(team_b)))
        extra_pitcher_order_bottom = list(range(len(team_a)))
        current_extra_top_index = 0
        current_extra_bottom_index = 0
        while inning <= 13 and score[team_a_name] == score[team_b_name]:
            # Top of extra inning:
            if not team_b:
                full_play_by_play.append(f"{team_b_name} has no players left! {team_a_name} wins by forfeit.")
                return full_play_by_play
            extra_pitcher_order_top = [i for i in extra_pitcher_order_top if i < len(team_b)]
            if not extra_pitcher_order_top:
                full_play_by_play.append(f"{team_b_name} has no pitchers left! {team_a_name} wins by forfeit.")
                return full_play_by_play
            pitcher_index = extra_pitcher_order_top[current_extra_top_index % len(extra_pitcher_order_top)]
            pitcher_top = team_b[pitcher_index]
            current_extra_top_index += 1
            defensive_positions_top = assign_defensive_positions([p for p in team_b if p != pitcher_top])
            defensive_positions_top["pitcher"] = pitcher_top
            full_play_by_play.append(f"=== Inning {inning}, Top: {team_a_name} Batting ===")
            full_play_by_play.append(f"⚾ Pitching for {team_b_name}: {pitcher_top.name} ⚾")
            inning_score_a, current_batter_a, play_by_play_a, forfeit_a = \
                half_inning_with_fixed_base_running(
                    team_a_name, team_a, pitcher_top, [], current_batter_a, inning, True,
                    team_a_name, team_b_name, defensive_positions_top, score, team_a, team_b,
                    foul_mood=foul_mood, riled_up=riled_up_a
                )
            full_play_by_play.extend(play_by_play_a)
            if forfeit_a:
                full_play_by_play.append(f"{team_a_name} has no players left! {team_b_name} wins by forfeit.")
                return full_play_by_play

            # Bottom of extra inning:
            if not team_a:
                full_play_by_play.append(f"{team_a_name} has no players left! {team_b_name} wins by forfeit.")
                return full_play_by_play
            extra_pitcher_order_bottom = [i for i in extra_pitcher_order_bottom if i < len(team_a)]
            if not extra_pitcher_order_bottom:
                full_play_by_play.append(f"{team_a_name} has no pitchers left! {team_b_name} wins by forfeit.")
                return full_play_by_play
            pitcher_index = extra_pitcher_order_bottom[current_extra_bottom_index % len(extra_pitcher_order_bottom)]
            pitcher_bottom = team_a[pitcher_index]
            current_extra_bottom_index += 1
            defensive_positions_bottom = assign_defensive_positions([p for p in team_a if p != pitcher_bottom])
            defensive_positions_bottom["pitcher"] = pitcher_bottom
            full_play_by_play.append(f"=== Inning {inning}, Bottom: {team_b_name} Batting ===")
            full_play_by_play.append(f"⚾ Pitching for {team_a_name}: {pitcher_bottom.name} ⚾")
            inning_score_b, current_batter_b, play_by_play_b, forfeit_b = \
                half_inning_with_fixed_base_running(
                    team_b_name, team_b, pitcher_bottom, [], current_batter_b, inning, False,
                    team_a_name, team_b_name, defensive_positions_bottom, score, team_a, team_b,
                    foul_mood=foul_mood, riled_up=riled_up_b, suppress_riled=False
                )
            full_play_by_play.extend(play_by_play_b)
            if forfeit_b:
                full_play_by_play.append(f"{team_b_name} has no players left! {team_a_name} wins by forfeit.")
                return full_play_by_play
            if score[team_a_name] != score[team_b_name]:
                break
            inning += 1
        if score[team_a_name] == score[team_b_name]:
            full_play_by_play.append("💀 Game tied at the end of the 13th inning. Everyone dies! 💀\n")
    else:
        full_play_by_play.append("🎉 Game Over! 🎉\n")
    full_play_by_play.append(f"📊 Final Score: {team_a_name}: {score[team_a_name]}, {team_b_name}: {score[team_b_name]}\n")
    if score[team_a_name] > score[team_b_name]:
        full_play_by_play.append(f"🏆 {team_a_name} wins! 🏆\n")
    elif score[team_b_name] > score[team_a_name]:
        full_play_by_play.append(f"🏆 {team_b_name} wins! 🏆\n")
    return full_play_by_play
