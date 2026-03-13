# DataGoal Development Log

## Project Overview
DataGoal is a football analytics and match prediction platform built as my CS50 Final Project. The aim is to go beyond simple football scores by providing prediction logic, player intelligence, and match-centered insights in a responsive web experience.

## Milestone 1: Repository and Project Setup
- Created the GitHub repository for DataGoal
- Connected the local VS Code project to GitHub
- Initialized Git and pushed the first commit
- Created the initial Flask project structure:
  - `app.py`
  - `predictor.py`
  - `api_client.py`
  - `schema.sql`
  - `templates/`
  - `static/`

## Milestone 2: Flask Environment Setup
- Created and activated a Python virtual environment
- Installed Flask
- Generated `requirements.txt`
- Added `.gitignore` to avoid committing unnecessary files

## Milestone 3: First Working Homepage
- Built the first working Flask homepage
- Confirmed the application runs on `127.0.0.1:5000`
- Verified template rendering works correctly

## Milestone 4: Debugging Templates and CSS
- Encountered blank-page issues due to template inheritance and layout setup
- Tested rendering using direct HTML in `app.py`
- Isolated the issue to template structure
- Rebuilt `layout.html`, `index.html`, and CSS step by step
- Confirmed static CSS files are being served correctly

## Milestone 5: Predictor Feature Prototype
- Created the first match predictor form
- Added user input fields for:
  - team names
  - wins in last 5 matches
  - goals scored
  - goals conceded
- Implemented basic prediction logic based on weighted score comparison

## Current Status
- Flask app is running successfully
- Homepage is rendering
- CSS is working
- Basic predictor feature exists
- Project is ready for premium UI enhancement and further modular cleanup