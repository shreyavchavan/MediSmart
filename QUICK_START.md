# Quick Start Guide

## Windows Users

### Step 1: Start the Backend
1. Double-click `start_backend.bat` OR
2. Open PowerShell/Command Prompt in the project folder and run:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

The backend will start on `http://localhost:8000`

### Step 2: Start the Frontend (in a new terminal)
1. Double-click `start_frontend.bat` OR
2. Open a new PowerShell/Command Prompt and run:
   ```bash
   cd frontend
   npm install
   npm start
   ```

The frontend will automatically open in your browser at `http://localhost:3000`

## macOS/Linux Users

### Step 1: Start the Backend
```bash
chmod +x start_backend.sh
./start_backend.sh
```

OR manually:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Step 2: Start the Frontend (in a new terminal)
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

OR manually:
```bash
cd frontend
npm install
npm start
```

## Usage

1. Once both servers are running, open `http://localhost:3000` in your browser
2. Click or drag and drop an image of a medicine (strip, bottle, or package)
3. Click "Analyze Medicine"
4. View the extracted information
5. Click "Download PDF Report" to save the report

## Troubleshooting

- **Backend won't start**: Make sure Python 3.8+ is installed
- **Frontend won't start**: Make sure Node.js 14+ is installed
- **CORS errors**: Ensure backend is running on port 8000
- **API errors**: Verify the Gemini API key is correct in `backend/main.py`

## Notes

- Keep both terminals open while using the application
- The backend must be running before the frontend can make requests
- First run may take longer due to dependency installation

