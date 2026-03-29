# Medicine Information Extractor

A full-stack web application that extracts text from medicine images (strips, bottles, packages) using AI and provides comprehensive medicine information including ingredients, uses, side effects, dosage, and age recommendations.

## Features

- 📸 **Image Upload**: Upload images of medicine strips, bottles, or packages
- 🔍 **AI-Powered OCR**: Extract text from images using Google Gemini Vision API
- 💊 **Medicine Information**: Get detailed information about medicines including:
  - Medicine name
  - Active ingredients
  - Medical uses/conditions
  - Side effects
  - Age recommendations
  - Dosage information (mg/ml)
  - Warnings and precautions
  - Storage instructions
- 📄 **PDF Report**: Download comprehensive PDF reports
- 🎨 **Modern UI**: Beautiful, responsive user interface

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI**: Web framework
- **Google Gemini API**: Vision and text generation
- **LangChain**: Structured data extraction
- **ReportLab**: PDF generation

### Frontend
- **React**: UI framework
- **Axios**: HTTP client
- **CSS3**: Modern styling with gradients and animations

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Start the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## API Endpoints

### POST `/api/analyze-medicine`
Upload an image file to extract medicine information.

**Request**: Multipart form data with `file` field
**Response**: JSON with extracted text and structured medicine information

### POST `/api/generate-pdf`
Generate a PDF report from medicine data.

**Request**: JSON with medicine information
**Response**: PDF file download

## Usage

1. Open the application in your browser (usually `http://localhost:3000`)
2. Click or drag and drop an image of a medicine strip/bottle/package
3. Click "Analyze Medicine" button
4. View the extracted information
5. Click "Download PDF Report" to save the information as a PDF

## Configuration

The API keys are currently hardcoded in `backend/main.py`:
- Gemini API Key: `AIzaSyA81BhVCBvHv_naFg1aflaPIcVw0k4cyXg`
- Image API Key: `xxyyzz`

For production, consider using environment variables.

## Project Structure

```
projectbyextration/
├── backend/
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── App.css         # Styles
│   │   └── index.js        # React entry point
│   └── package.json        # Node dependencies
└── README.md
```

## Important Notes

⚠️ **Disclaimer**: This application provides information for educational purposes only. Always consult with a healthcare professional before taking any medication.

## Troubleshooting

- If the backend fails to start, ensure all Python dependencies are installed
- If CORS errors occur, check that the frontend URL is added to CORS origins in `main.py`
- If image processing fails, verify the Gemini API key is valid
- For PDF generation issues, ensure ReportLab is properly installed

## License

This project is for educational purposes.

