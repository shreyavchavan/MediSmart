#!/bin/bash
echo "Starting Backend Server..."
cd backend
python3 -m venv venv 2>/dev/null
source venv/bin/activate
pip install -r requirements.txt
python main.py

