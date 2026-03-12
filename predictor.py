def calculate_prediction(
    home_team,
    away_team,
    home_wins,
    away_wins,
    home_goals_for,
    away_goals_for,
    home_goals_against,
    away_goals_against,
):
    home_score = (home_wins * 3) + home_goals_for - home_goals_against + 1
    away_score = (away_wins * 3) + away_goals_for - away_goals_against

    if home_score > away_score:
        result = f"{home_team} is more likely to win."
    elif away_score > home_score:
        result = f"{away_team} is more likely to win."
    else:
        result = "This match looks balanced and may end in a draw."

    return home_score, away_score, result