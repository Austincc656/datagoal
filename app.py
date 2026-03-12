from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return """
    <h1>DataGoal is working</h1>
    <p>Beyond the Scoreline</p>
    <a href="/predict">Go to Predictor</a>
    """


@app.route("/predict")
def predict():
    return render_template("predict.html")


@app.route("/player")
def player():
    return render_template("player.html")


@app.route("/match")
def match():
    return render_template("match.html")


if __name__ == "__main__":
    app.run(debug=True)