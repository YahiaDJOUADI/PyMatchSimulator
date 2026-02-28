PyMatchSimulator

PyMatchSimulator is a simple Python desktop app to simulate football matches and manage teams. Built with CustomTkinter for a clean and modern UI.

⚽ The project idea and many gameplay features were inspired by the EA Sports FC game.
🤖 AI tools were used to assist with parts of the UI design and interface styling.

Features
Match Simulation

Simulate realistic matches with goals, xG, VAR decisions, substitutions, offsides, injuries, and tactics.

Team Management

Manage players, formations, match ratings, and career stats.

Competitions

Play single matches, leagues, or tournaments.

Stats & Rankings

Track ELO ratings, top scorers, assists, appearances, and match history.

Modern UI

Dark mode dashboard with live commentary, tactical pitch view, results screen, and custom team badges.

Project Structure

models/ – Player, Team, and Match classes

engine/ – Core simulation logic (simulator.py)

utils/ – Data loading and match history management

Getting Started
1. Install Dependencies
pip install customtkinter pillow
2. Run the Project
python main.py