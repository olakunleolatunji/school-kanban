@echo off
:: This script launches your Kanban board automatically

:: 1. Navigate strictly to your project folder
cd /d "C:\Users\elnuk\Documents\kanban_project"

:: 2. Activate the virtual environment
call venv\Scripts\activate

:: 3. Open the Kanban board using your custom name
start http://schoolkanban:5000

:: 4. Run the Flask application
python app.py