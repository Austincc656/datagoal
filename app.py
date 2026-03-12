from flask import Flask, render_template, request
from predictor import calculate_prediction

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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


if __name__ == "__main__":
    app.run(debug=True)