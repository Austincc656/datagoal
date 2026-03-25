import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = "e4f616a65a663d3625638b8e2e219c9d"
BASE_URL = "https://v3.football.api-sports.io"


def api_headers():
    return {
        "x-apisports-key": API_KEY
    }


# =========================
# GENERAL HELPERS
# =========================
def calculate_form_score(matches):
    score = 0
    for match in matches:
        result = match.get("result", "L")
        if result == "W":
            score += 3
        elif result == "D":
            score += 1
    return score


def extract_stat_value(stats_list, stat_name):
    for item in stats_list:
        if item.get("type") == stat_name:
            return item.get("value")
    return None


# =========================
# STATIC / STRUCTURED DATA
# =========================
def get_available_sample_teams():
    return {
        "Premier League": [
            "Liverpool",
            "Arsenal",
            "Manchester City",
            "Chelsea",
            "Manchester United",
            "Tottenham",
            "Aston Villa"
        ],
        "La Liga": [
            "Real Madrid",
            "Barcelona",
            "Atletico Madrid",
            "Real Sociedad"
        ],
        "Bundesliga": [
            "Bayern Munich",
            "Borussia Dortmund",
            "Bayer Leverkusen",
            "RB Leipzig"
        ]
    }


def get_barcelona_info():
    return {
        "name": "FC Barcelona",
        "founded": 1899,
        "stadium": "Spotify Camp Nou",
        "description": (
            "FC Barcelona is one of the most successful football clubs in the world, "
            "known for its possession-based playing style and strong football identity. "
            "The club is famous for legendary players such as Lionel Messi, Xavi, and Iniesta, "
            "and for developing elite talent through La Masia."
        ),
        "logo": "https://media.api-sports.io/football/teams/529.png"
    }


def get_featured_barcelona_players():
    return [
        {
            "name": "Lamine Yamal",
            "role": "Right Winger",
            "tag": "Creative Spark",
            "description": "A highly dynamic attacker known for direct dribbling, flair, and fast decision-making in wide areas.",
            "image": "https://img.a.transfermarkt.technology/portrait/header/937958-1699474078.jpg"
        },
        {
            "name": "Pedri",
            "role": "Midfielder",
            "tag": "Control Engine",
            "description": "Brings tempo control, positional intelligence, and smooth progression through midfield.",
            "image": "https://img.a.transfermarkt.technology/portrait/header/683840-1699473534.jpg"
        },
        {
            "name": "Robert Lewandowski",
            "role": "Striker",
            "tag": "Goal Threat",
            "description": "Provides elite finishing, penalty-box movement, and strong attacking leadership.",
            "image": "https://img.a.transfermarkt.technology/portrait/header/38253-1699473739.jpg"
        }
    ]


def get_team_last_matches(team_name):
    """
    Structured fallback recent form for prediction logic.
    This is separate from live data and supports the prediction engine.
    """
    samples = {
        "Manchester City": [{"result": "W"}, {"result": "W"}, {"result": "D"}, {"result": "W"}, {"result": "W"}],
        "Arsenal": [{"result": "W"}, {"result": "D"}, {"result": "W"}, {"result": "L"}, {"result": "W"}],
        "Chelsea": [{"result": "D"}, {"result": "L"}, {"result": "W"}, {"result": "D"}, {"result": "L"}],
        "Liverpool": [{"result": "W"}, {"result": "W"}, {"result": "W"}, {"result": "D"}, {"result": "W"}],
        "Manchester United": [{"result": "W"}, {"result": "L"}, {"result": "D"}, {"result": "W"}, {"result": "L"}],
        "Tottenham": [{"result": "W"}, {"result": "D"}, {"result": "W"}, {"result": "W"}, {"result": "L"}],
        "Aston Villa": [{"result": "W"}, {"result": "W"}, {"result": "L"}, {"result": "D"}, {"result": "W"}],
        "Barcelona": [{"result": "W"}, {"result": "W"}, {"result": "W"}, {"result": "W"}, {"result": "D"}],
        "Real Madrid": [{"result": "W"}, {"result": "W"}, {"result": "D"}, {"result": "W"}, {"result": "W"}],
        "Atletico Madrid": [{"result": "W"}, {"result": "D"}, {"result": "W"}, {"result": "L"}, {"result": "W"}],
        "Real Sociedad": [{"result": "D"}, {"result": "W"}, {"result": "L"}, {"result": "W"}, {"result": "D"}],
        "Bayern Munich": [{"result": "W"}, {"result": "D"}, {"result": "W"}, {"result": "W"}, {"result": "L"}],
        "Borussia Dortmund": [{"result": "D"}, {"result": "W"}, {"result": "L"}, {"result": "W"}, {"result": "D"}],
        "Bayer Leverkusen": [{"result": "W"}, {"result": "W"}, {"result": "W"}, {"result": "D"}, {"result": "W"}],
        "RB Leipzig": [{"result": "W"}, {"result": "L"}, {"result": "W"}, {"result": "D"}, {"result": "W"}],
    }

    return samples.get(
        team_name,
        [{"result": "W"}, {"result": "D"}, {"result": "L"}, {"result": "W"}, {"result": "D"}]
    )


def get_standings_table(league_name):
    """
    Structured fallback standings for prediction logic.
    """
    league_name = (league_name or "").lower()

    premier_league = {
        "Liverpool": {"points": 72, "goal_diff": 39, "position": 1},
        "Arsenal": {"points": 68, "goal_diff": 31, "position": 2},
        "Manchester City": {"points": 65, "goal_diff": 28, "position": 3},
        "Aston Villa": {"points": 56, "goal_diff": 15, "position": 4},
        "Manchester United": {"points": 51, "goal_diff": 4, "position": 5},
        "Chelsea": {"points": 47, "goal_diff": 3, "position": 6},
        "Tottenham": {"points": 45, "goal_diff": 7, "position": 7}
    }

    la_liga = {
        "Real Madrid": {"points": 75, "goal_diff": 40, "position": 1},
        "Barcelona": {"points": 70, "goal_diff": 33, "position": 2},
        "Atletico Madrid": {"points": 62, "goal_diff": 22, "position": 3},
        "Real Sociedad": {"points": 52, "goal_diff": 12, "position": 4}
    }

    bundesliga = {
        "Bayer Leverkusen": {"points": 69, "goal_diff": 37, "position": 1},
        "Bayern Munich": {"points": 67, "goal_diff": 35, "position": 2},
        "Borussia Dortmund": {"points": 59, "goal_diff": 20, "position": 3},
        "RB Leipzig": {"points": 57, "goal_diff": 18, "position": 4}
    }

    if "premier" in league_name:
        return premier_league
    if "liga" in league_name:
        return la_liga
    if "bundesliga" in league_name:
        return bundesliga

    combined = {}
    combined.update(premier_league)
    combined.update(la_liga)
    combined.update(bundesliga)
    return combined


def get_head_to_head_summary(home_team, away_team):
    pairs = {
        ("Manchester City", "Arsenal"): {"home_wins": 2, "away_wins": 1, "draws": 2},
        ("Arsenal", "Manchester City"): {"home_wins": 1, "away_wins": 2, "draws": 2},
        ("Liverpool", "Manchester United"): {"home_wins": 3, "away_wins": 1, "draws": 1},
        ("Manchester United", "Liverpool"): {"home_wins": 1, "away_wins": 3, "draws": 1},
        ("Real Madrid", "Barcelona"): {"home_wins": 2, "away_wins": 2, "draws": 1},
        ("Barcelona", "Real Madrid"): {"home_wins": 2, "away_wins": 2, "draws": 1},
        ("Bayern Munich", "Borussia Dortmund"): {"home_wins": 3, "away_wins": 1, "draws": 1},
        ("Borussia Dortmund", "Bayern Munich"): {"home_wins": 1, "away_wins": 3, "draws": 1},
        ("Bayer Leverkusen", "Bayern Munich"): {"home_wins": 2, "away_wins": 2, "draws": 1},
        ("Bayern Munich", "Bayer Leverkusen"): {"home_wins": 2, "away_wins": 2, "draws": 1},
    }

    return pairs.get((home_team, away_team), {"home_wins": 1, "away_wins": 1, "draws": 3})


def get_team_strength_snapshot(team_name, standings, recent_matches):
    team_table = standings.get(team_name, {"points": 0, "goal_diff": 0, "position": 20})
    return {
        "team": team_name,
        "form_score": calculate_form_score(recent_matches),
        "points": team_table.get("points", 0),
        "goal_diff": team_table.get("goal_diff", 0),
        "position": team_table.get("position", 20)
    }


# =========================
# LIVE DATA HELPERS
# =========================
def get_fixture_stats(fixture_id):
    """
    Returns live match statistics for a fixture, or None if unavailable.
    """
    if not API_KEY:
        return None

    try:
        url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"
        response = requests.get(url, headers=api_headers(), timeout=12)
        response.raise_for_status()
        data = response.json()

        response_items = data.get("response", [])
        if len(response_items) < 2:
            return None

        home_item = response_items[0]
        away_item = response_items[1]

        home_stats_list = home_item.get("statistics", [])
        away_stats_list = away_item.get("statistics", [])

        return {
            "home": {
                "possession": extract_stat_value(home_stats_list, "Ball Possession") or "-",
                "shots_on_target": extract_stat_value(home_stats_list, "Shots on Goal") or "-",
                "total_shots": extract_stat_value(home_stats_list, "Total Shots") or "-",
                "corners": extract_stat_value(home_stats_list, "Corner Kicks") or "-"
            },
            "away": {
                "possession": extract_stat_value(away_stats_list, "Ball Possession") or "-",
                "shots_on_target": extract_stat_value(away_stats_list, "Shots on Goal") or "-",
                "total_shots": extract_stat_value(away_stats_list, "Total Shots") or "-",
                "corners": extract_stat_value(away_stats_list, "Corner Kicks") or "-"
            }
        }

    except Exception:
        return None


def get_fixture_lineups(fixture_id):
    """
    Returns lineups for a fixture, or None if unavailable.
    """
    if not API_KEY:
        return None

    try:
        url = f"{BASE_URL}/fixtures/lineups?fixture={fixture_id}"
        response = requests.get(url, headers=api_headers(), timeout=12)
        response.raise_for_status()
        data = response.json()

        response_items = data.get("response", [])
        if len(response_items) < 2:
            return None

        home = response_items[0]
        away = response_items[1]

        return {
            "home": {
                "team_name": home.get("team", {}).get("name", "Unknown"),
                "team_logo": home.get("team", {}).get("logo"),
                "formation": home.get("formation", "-"),
                "coach": home.get("coach", {}).get("name", "-"),
                "start_xi": [
                    player.get("player", {}).get("name", "-")
                    for player in home.get("startXI", [])
                ],
                "substitutes": [
                    player.get("player", {}).get("name", "-")
                    for player in home.get("substitutes", [])
                ]
            },
            "away": {
                "team_name": away.get("team", {}).get("name", "Unknown"),
                "team_logo": away.get("team", {}).get("logo"),
                "formation": away.get("formation", "-"),
                "coach": away.get("coach", {}).get("name", "-"),
                "start_xi": [
                    player.get("player", {}).get("name", "-")
                    for player in away.get("startXI", [])
                ],
                "substitutes": [
                    player.get("player", {}).get("name", "-")
                    for player in away.get("substitutes", [])
                ]
            }
        }

    except Exception:
        return None


def get_team_recent_form_from_name(team_name):
    recent = get_team_last_matches(team_name)
    return [match.get("result", "-") for match in recent]


def get_live_match_center_data():
    """
    Real live match data only.
    Returns [] if:
    - no API key
    - no live fixtures
    - API error
    """
    if not API_KEY:
        return []

    try:
        url = f"{BASE_URL}/fixtures?live=all"
        response = requests.get(url, headers=api_headers(), timeout=12)
        response.raise_for_status()
        data = response.json()

        fixtures = data.get("response", [])
        if not fixtures:
            return []

        enriched_matches = []

        for item in fixtures[:6]:
            fixture = item.get("fixture", {})
            teams = item.get("teams", {})
            goals = item.get("goals", {})
            league = item.get("league", {})
            fixture_id = fixture.get("id")

            stats_data = get_fixture_stats(fixture_id) if fixture_id else None
            lineup_data = get_fixture_lineups(fixture_id) if fixture_id else None

            home_name = teams.get("home", {}).get("name", "Unknown")
            away_name = teams.get("away", {}).get("name", "Unknown")

            enriched_matches.append({
                "fixture_id": fixture_id,
                "league": league.get("name", "Unknown League"),
                "country": league.get("country", ""),
                "status": fixture.get("status", {}).get("short", "NS"),
                "elapsed": fixture.get("status", {}).get("elapsed"),
                "home_team": home_name,
                "away_team": away_name,
                "home_logo": teams.get("home", {}).get("logo"),
                "away_logo": teams.get("away", {}).get("logo"),
                "home_goals": goals.get("home"),
                "away_goals": goals.get("away"),
                "home_stats": (stats_data or {}).get("home", {
                    "possession": "-",
                    "shots_on_target": "-",
                    "total_shots": "-",
                    "corners": "-"
                }),
                "away_stats": (stats_data or {}).get("away", {
                    "possession": "-",
                    "shots_on_target": "-",
                    "total_shots": "-",
                    "corners": "-"
                }),
                "home_recent_form": get_team_recent_form_from_name(home_name),
                "away_recent_form": get_team_recent_form_from_name(away_name),
                "lineups": lineup_data or {
                    "home": {
                        "team_name": home_name,
                        "team_logo": teams.get("home", {}).get("logo"),
                        "formation": "-",
                        "coach": "-",
                        "start_xi": [],
                        "substitutes": []
                    },
                    "away": {
                        "team_name": away_name,
                        "team_logo": teams.get("away", {}).get("logo"),
                        "formation": "-",
                        "coach": "-",
                        "start_xi": [],
                        "substitutes": []
                    }
                }
            })

        return enriched_matches

    except Exception:
        return []