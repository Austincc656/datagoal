#i used claude ai to improve the app.py file, which is the main application file for the datagoal football prediction website.
#the improvements include:
#1. Refactored the code to improve readability and maintainability, including better organization of functions and routes.
#2. Added more detailed comments and docstrings to explain the purpose of functions and code blocks


import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from api_client import (
    get_team_last_matches,
    get_standings_table,
    get_head_to_head_summary,
    get_team_strength_snapshot,
    get_available_sample_teams,
    get_featured_barcelona_players,
    get_barcelona_info,
    get_live_match_center_data
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "datagoal_dev_secret")

DATABASE = "datagoal.db"


# =========================
# DATABASE HELPERS
# =========================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            hash TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            league TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            prediction TEXT NOT NULL,
            confidence INTEGER NOT NULL,
            reasons TEXT NOT NULL,
            home_form_score REAL DEFAULT 0,
            away_form_score REAL DEFAULT 0,
            home_table_points INTEGER DEFAULT 0,
            away_table_points INTEGER DEFAULT 0,
            home_strength REAL DEFAULT 0,
            away_strength REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# CACHE CONTROL
# =========================
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response


# =========================
# AUTH HELPERS
# =========================
def login_required():
    if "user_id" not in session:
        flash("Please log in to use the prediction tool and save your results.")
        return False
    return True


# =========================
# CORE PREDICTION LOGIC
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


def normalize_strength(form_score, table_points, goal_diff, position):
    position_score = max(0, 25 - position) if position else 0
    return round(
        (form_score * 2.5) +
        (table_points * 0.4) +
        (goal_diff * 0.35) +
        (position_score * 0.8),
        2
    )


def predict_match(home_team, away_team, league_name, home_recent, away_recent, standings, h2h):
    home_form_score = calculate_form_score(home_recent)
    away_form_score = calculate_form_score(away_recent)

    home_table = standings.get(home_team, {"points": 0, "goal_diff": 0, "position": 20})
    away_table = standings.get(away_team, {"points": 0, "goal_diff": 0, "position": 20})

    home_points = home_table.get("points", 0)
    away_points = away_table.get("points", 0)

    home_goal_diff = home_table.get("goal_diff", 0)
    away_goal_diff = away_table.get("goal_diff", 0)

    home_position = home_table.get("position", 20)
    away_position = away_table.get("position", 20)

    home_h2h_wins = h2h.get("home_wins", 0)
    away_h2h_wins = h2h.get("away_wins", 0)

    home_strength = normalize_strength(
        form_score=home_form_score,
        table_points=home_points,
        goal_diff=home_goal_diff,
        position=home_position
    )

    away_strength = normalize_strength(
        form_score=away_form_score,
        table_points=away_points,
        goal_diff=away_goal_diff,
        position=away_position
    )

    # home advantage
    home_strength += 3.5

    reasons = []

    if home_form_score > away_form_score:
        reasons.append(f"{home_team} has the stronger recent form.")
    elif away_form_score > home_form_score:
        reasons.append(f"{away_team} has the stronger recent form.")
    else:
        reasons.append("Both teams have similar recent form.")

    if home_points > away_points:
        reasons.append(f"{home_team} is stronger in the league table.")
    elif away_points > home_points:
        reasons.append(f"{away_team} is stronger in the league table.")
    else:
        reasons.append("Both teams are close in league table points.")

    if home_goal_diff > away_goal_diff:
        reasons.append(f"{home_team} has the better goal difference.")
    elif away_goal_diff > home_goal_diff:
        reasons.append(f"{away_team} has the better goal difference.")

    if home_position < away_position:
        reasons.append(f"{home_team} is placed higher in the standings.")
    elif away_position < home_position:
        reasons.append(f"{away_team} is placed higher in the standings.")

    if home_h2h_wins > away_h2h_wins:
        reasons.append(f"{home_team} has a stronger recent head-to-head record.")
    elif away_h2h_wins > home_h2h_wins:
        reasons.append(f"{away_team} has a stronger recent head-to-head record.")
    else:
        reasons.append("Recent head-to-head record is balanced.")

    reasons.append(f"{home_team} benefits from home advantage.")

    diff = round(abs(home_strength - away_strength), 2)

    if diff <= 4:
        prediction = "Draw"
        confidence = 56
    elif home_strength > away_strength:
        prediction = f"{home_team} Win"
        confidence = min(88, int(58 + diff * 1.7))
    else:
        prediction = f"{away_team} Win"
        confidence = min(88, int(58 + diff * 1.7))

    return {
        "prediction": prediction,
        "confidence": confidence,
        "reasons": " ".join(reasons),
        "home_form_score": home_form_score,
        "away_form_score": away_form_score,
        "home_table_points": home_points,
        "away_table_points": away_points,
        "home_goal_diff": home_goal_diff,
        "away_goal_diff": away_goal_diff,
        "home_position": home_position,
        "away_position": away_position,
        "home_strength": round(home_strength, 2),
        "away_strength": round(away_strength, 2),
        "home_h2h_wins": home_h2h_wins,
        "away_h2h_wins": away_h2h_wins,
        "draws": h2h.get("draws", 0)
    }


# =========================
# PUBLIC ROUTES
# =========================
@app.route("/")
def index():
    featured_players = get_featured_barcelona_players()
    barcelona = get_barcelona_info()

    return render_template(
        "index.html",
        featured_players=featured_players,
        barcelona=barcelona
    )


@app.route("/live")
def live():
    live_matches = get_live_match_center_data()
    return render_template("live.html", live_matches=live_matches)


# =========================
# AUTH ROUTES
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not username:
            flash("Username is required.")
            return redirect("/register")

        if not password:
            flash("Password is required.")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")

        conn = get_db_connection()
        cursor = conn.cursor()

        existing = cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()
            flash("Username already exists.")
            return redirect("/register")

        password_hash = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (username, password_hash)
        )

        conn.commit()
        conn.close()

        flash("Registration successful. Please log in.")
        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username:
            flash("Username is required.")
            return redirect("/login")

        if not password:
            flash("Password is required.")
            return redirect("/login")

        conn = get_db_connection()
        cursor = conn.cursor()

        user = cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password.")
            return redirect("/login")

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        flash("Logged in successfully.")
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect("/")


# =========================
# PROTECTED ROUTES
# =========================
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if not login_required():
        return redirect("/login")

    teams_by_league = get_available_sample_teams()

    if request.method == "POST":
        league = request.form.get("league", "").strip()
        home_team = request.form.get("home_team", "").strip()
        away_team = request.form.get("away_team", "").strip()

        if not league:
            flash("League is required.")
            return redirect("/predict")

        if not home_team or not away_team:
            flash("Both teams are required.")
            return redirect("/predict")

        if home_team.lower() == away_team.lower():
            flash("Home team and away team must be different.")
            return redirect("/predict")

        home_recent = get_team_last_matches(home_team)
        away_recent = get_team_last_matches(away_team)
        standings = get_standings_table(league)
        h2h = get_head_to_head_summary(home_team, away_team)

        result = predict_match(
            home_team=home_team,
            away_team=away_team,
            league_name=league,
            home_recent=home_recent,
            away_recent=away_recent,
            standings=standings,
            h2h=h2h
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO predictions (
                user_id, league, home_team, away_team, prediction, confidence, reasons,
                home_form_score, away_form_score, home_table_points, away_table_points,
                home_strength, away_strength, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            league,
            home_team,
            away_team,
            result["prediction"],
            result["confidence"],
            result["reasons"],
            result["home_form_score"],
            result["away_form_score"],
            result["home_table_points"],
            result["away_table_points"],
            result["home_strength"],
            result["away_strength"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return redirect(f"/result/{prediction_id}")

    return render_template("predict.html", teams_by_league=teams_by_league)


@app.route("/result/<int:prediction_id>")
def result(prediction_id):
    if not login_required():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    prediction = cursor.execute("""
        SELECT * FROM predictions
        WHERE id = ? AND user_id = ?
    """, (prediction_id, session["user_id"])).fetchone()

    conn.close()

    if prediction is None:
        flash("Prediction not found.")
        return redirect("/history")

    home_recent = get_team_last_matches(prediction["home_team"])
    away_recent = get_team_last_matches(prediction["away_team"])
    h2h = get_head_to_head_summary(prediction["home_team"], prediction["away_team"])

    return render_template(
        "result.html",
        prediction=prediction,
        home_recent=home_recent,
        away_recent=away_recent,
        h2h=h2h
    )


@app.route("/history")
def history():
    if not login_required():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    predictions = cursor.execute("""
        SELECT * FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template("history.html", predictions=predictions)


@app.route("/insights")
def insights():
    if not login_required():
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    predictions = cursor.execute("""
        SELECT * FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (session["user_id"],)).fetchall()

    conn.close()

    total_predictions = len(predictions)
    home_win_count = 0
    away_win_count = 0
    draw_count = 0
    highest_confidence = 0
    average_confidence = 0
    most_predicted_league = "N/A"
    most_featured_team = "N/A"

    league_counts = {}
    team_counts = {}
    confidence_total = 0

    for row in predictions:
        prediction_text = row["prediction"]

        if prediction_text == "Draw":
            draw_count += 1
        elif prediction_text == f"{row['home_team']} Win":
            home_win_count += 1
        elif prediction_text == f"{row['away_team']} Win":
            away_win_count += 1

        if row["confidence"] > highest_confidence:
            highest_confidence = row["confidence"]

        confidence_total += row["confidence"]

        league_counts[row["league"]] = league_counts.get(row["league"], 0) + 1
        team_counts[row["home_team"]] = team_counts.get(row["home_team"], 0) + 1
        team_counts[row["away_team"]] = team_counts.get(row["away_team"], 0) + 1

    if total_predictions > 0:
        average_confidence = round(confidence_total / total_predictions, 1)

    if league_counts:
        most_predicted_league = max(league_counts, key=league_counts.get)

    if team_counts:
        most_featured_team = max(team_counts, key=team_counts.get)

    return render_template(
        "insights.html",
        total_predictions=total_predictions,
        home_win_count=home_win_count,
        away_win_count=away_win_count,
        draw_count=draw_count,
        highest_confidence=highest_confidence,
        average_confidence=average_confidence,
        most_predicted_league=most_predicted_league,
        most_featured_team=most_featured_team
    )


# =========================
# AJAX / API ROUTES
# =========================
@app.route("/api/team-stats")
def api_team_stats():
    league = request.args.get("league", "").strip()
    home_team = request.args.get("home_team", "").strip()
    away_team = request.args.get("away_team", "").strip()

    if not league or not home_team or not away_team:
        return jsonify({
            "success": False,
            "message": "League, home team, and away team are required."
        }), 400

    standings = get_standings_table(league)
    home_recent = get_team_last_matches(home_team)
    away_recent = get_team_last_matches(away_team)
    h2h = get_head_to_head_summary(home_team, away_team)

    home_snapshot = get_team_strength_snapshot(home_team, standings, home_recent)
    away_snapshot = get_team_strength_snapshot(away_team, standings, away_recent)

    return jsonify({
        "success": True,
        "league": league,
        "home_team": {
            "name": home_team,
            "form_score": home_snapshot["form_score"],
            "points": home_snapshot["points"],
            "goal_diff": home_snapshot["goal_diff"],
            "position": home_snapshot["position"],
            "recent_form": [match["result"] for match in home_recent]
        },
        "away_team": {
            "name": away_team,
            "form_score": away_snapshot["form_score"],
            "points": away_snapshot["points"],
            "goal_diff": away_snapshot["goal_diff"],
            "position": away_snapshot["position"],
            "recent_form": [match["result"] for match in away_recent]
        },
        "head_to_head": h2h
    })


@app.route("/api/teams")
def api_teams():
    teams_by_league = get_available_sample_teams()
    return jsonify({
        "success": True,
        "teams_by_league": teams_by_league
    })


# =========================
# ERROR HANDLERS
# =========================
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)