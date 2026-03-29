@echo off
echo Starting Backend Server...
cd backend
python -m venv venv 2>nul
call venv\Scripts\activate
pip install -r requirements.txt
python main.py
pause

