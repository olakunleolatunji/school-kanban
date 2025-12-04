@echo off
:: This script launches your Kanban board server ONLY (no browser popup)

:: 1. Navigate strictly to your project folder
cd /d "C:\Users\elnuk\Documents\kanban_project"

:: 2. Activate the virtual environment
call venv\Scripts\activate

:: 3. Run the Flask application
:: The server will start, but no window will open.
:: You can access it anytime at http://schoolkanban:5000
python app.py