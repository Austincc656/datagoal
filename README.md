# DataGoal: Beyond the Scoreline

## video Demo: https://youtu.be/qyBpSmh0H_s

## Overview

DataGoal: Beyond the Scoreline is a football analytics web application built as my CS50 2026 final project. The goal of the project is to go beyond basic football score viewing by combining live football intelligence, explainable match prediction logic, and user-based analytics in one platform.

The application allows users to browse real-time football match information publicly, while requiring authentication for personalized prediction features. It integrates football data, team comparison logic, live match context, and user history tracking into a single web-based product.

This project was designed not just as a football app, but as a lightweight decision-support system that transforms football-related data into interpretable insights.

---

## Project Idea

Most football apps focus only on scorelines, fixtures, or live commentary. DataGoal takes a different approach by combining:

- live football match monitoring
- team performance context
- prediction logic
- saved user prediction history
- analytics and insights

The aim is to create a system that helps users understand not only *what is happening*, but also *why a match outcome may be likely*.

---

## Main Features

### 1. Public Homepage
The homepage introduces the DataGoal concept and presents a premium football analytics identity. It also includes a Barcelona-focused section with club information and featured players for storytelling and visual engagement.

### 2. Live Match Center
The Live Match Center allows users to browse real football match data without logging in. It displays:
- live scores
- league and country information
- club logos where available
- match statistics such as possession, shots, and corners
- formations and coaches where available
- starting lineups and substitutes where available
- recent form indicators

If there are no live matches available from the API, the application honestly shows an empty-state message rather than fake or assumed data.

### 3. Prediction Tool
Authenticated users can use the prediction tool to generate match outcome predictions. The system compares:
- recent team form
- standings
- goal difference
- position in the table
- head-to-head summary
- home advantage

The app then returns a prediction with a confidence level and an explanation.

### 4. Prediction History
Each generated prediction is saved to the database and can be reviewed later by the logged-in user.

### 5. Insights Dashboard
The insights page summarizes user prediction activity, including:
- total predictions
- number of home-win predictions
- number of away-win predictions
- draw predictions
- highest confidence prediction
- average confidence
- most predicted league
- most featured team

---

## Technologies Used

- **Python**
- **Flask**
- **SQLite**
- **HTML**
- **CSS**
- **JavaScript**
- **API-Football / API-Sports**
- **python-dotenv**
- **Werkzeug**

---

## Project Structure

datagoal/
│
├── app.py
├── api_client.py
├── requirements.txt
├── README.md
├── .gitignore
├── schema.sql
│
├── static/
│   ├── styles.css
│   └── main.js
│
├── templates/
│   ├── layout.html
│   ├── index.html
│   ├── live.html
│   ├── predict.html
│   ├── result.html
│   ├── history.html
│   ├── insights.html
│   ├── login.html
│   ├── register.html
│   ├── 404.html
│   └── 500.html