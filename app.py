from unittest import result

from flask import Flask, render_template, request
from predictor import calculate_prediction
from api_client import get_live_matches, get_today_fixtures
import sqlite3
DATABASE = "predictions.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        home_team TEXT NOT NULL,
        away_team TEXT NOT NULL,
        home_score INTEGER NOT NULL,
        away_score INTEGER NOT NULL,
        result TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live")
def live():
    try:
        live_matches = get_live_matches()

        if live_matches.get("response") and len(live_matches["response"]) > 0:
            return render_template(
                "live.html",
                matches=live_matches["response"],
                page_title="Live Matches"
            )

        today_fixtures = get_today_fixtures()
        return render_template(
            "live.html",
            matches=today_fixtures["response"],
            page_title="Today's Fixtures"
        )

    except Exception as e:
        return f"<h1>Live Matches Error</h1><p>{str(e)}</p>"
    
@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        home_team = request.form.get("home_team")
        away_team = request.form.get("away_team")

        home_wins = int(request.form.get("home_wins"))
        away_wins = int(request.form.get("away_wins"))

        home_goals_for = int(request.form.get("home_goals_for"))
        away_goals_for = int(request.form.get("away_goals_for"))

        home_goals_against = int(request.form.get("home_goals_against"))
        away_goals_against = int(request.form.get("away_goals_against"))

        home_score, away_score, result = calculate_prediction(
            home_team,
            away_team,
            home_wins,
            away_wins,
            home_goals_for,
            away_goals_for,
            home_goals_against,
            away_goals_against,
        )
        
        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO predictions (home_team, away_team, home_score, away_score, result)
            VALUES (?, ?, ?, ?, ?)
            """,
            (home_team, away_team, home_score, away_score, result),
        )

        conn.commit()
        conn.close()

        total = home_score + away_score
        if total <= 0:
            home_prob = 33
            away_prob = 33
            draw_prob = 34
        else:
            home_prob = round((home_score / total) * 100)
            away_prob = round((away_score / total) * 100)
            draw_prob = max(0, 100 - home_prob - away_prob)

        return render_template(
            "result.html",
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            result=result,
            home_prob=home_prob,
            away_prob=away_prob,
            draw_prob=draw_prob,
            home_wins=home_wins,
            away_wins=away_wins,
            home_goals_for=home_goals_for,
            away_goals_for=away_goals_for,
            home_goals_against=home_goals_against,
            away_goals_against=away_goals_against,
        )

    return render_template("predict.html")


@app.route("/player")
def player():
    return render_template("player.html")


@app.route("/match")
def match():
    return render_template("match.html")

@app.route("/history")
def history():
    conn = get_db_connection()

    predictions = conn.execute(
        """
        SELECT *
        FROM predictions
        ORDER BY created_at DESC
        """
    ).fetchall()

    conn.close()

    return render_template("history.html", predictions=predictions)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)