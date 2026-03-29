from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime
import json

app = FastAPI(title="Medicine Information Extractor")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyA81BhVCBvHv_naFg1aflaPIcVw0k4cyXg"
IMAGE_API_KEY = "xxyyzz"
genai.configure(api_key=GEMINI_API_KEY)

# Initialize LangChain with Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)

# Pydantic models for structured output
# Pydantic models for structured output
class MedicineInfo(BaseModel):
    medicine_name: str = Field(description="Full commercial name of the medicine including strength if visible")
    active_ingredients: List[str] = Field(description="Detailed list of active ingredients with their concentrations if available")
    uses: List[str] = Field(description="Comprehensive list of medical conditions, diseases, or symptoms this medicine is used to treat")
    side_effects: List[str] = Field(description="Comprehensive list of potential side effects, categorized if possible (common, rare, etc.)")
    age_recommendation: str = Field(description="Detailed age recommendations, contraindications for children/elderly, and specific age groups allowed")
    dosage: str = Field(description="Detailed dosage instructions including frequency, timing (before/after food), and duration if specified")
    warnings: Optional[List[str]] = Field(default=[], description="Critical warnings, contraindications (e.g., pregnancy, driving), and drug interactions")
    storage: Optional[str] = Field(default="", description="Specific storage instructions including temperature and light conditions")
    manufacturer: Optional[str] = Field(default="", description="Name of the pharmaceutical company/manufacturer")
    batch_number: Optional[str] = Field(default="", description="Batch number or Lot number if visible")
    expiry_date: Optional[str] = Field(default="", description="Expiry date if visible")

class MedicineResponse(BaseModel):
    extracted_text: str
    medicine_info: MedicineInfo

class InteractionRequest(BaseModel):
    medicines: List[str]

class InteractionDetail(BaseModel):
    severity: str = Field(description="Severity of interaction: 'Safe', 'Caution', or 'Dangerous'")
    explanation: str = Field(description="Detailed explanation of the interaction")
    harmful_effects: Optional[List[str]] = Field(default=[], description="List of potential harmful effects or reactions")
    advice: str = Field(description="Medical advice or instructions (e.g., 'take 2 hours apart', 'avoid combination')")

class InteractionResponse(BaseModel):
    overall_status: str
    interactions: List[InteractionDetail]
    disclaimer: str

# Output parser for interactions
interaction_parser = PydanticOutputParser(pydantic_object=InteractionResponse)

# Output parser
parser = PydanticOutputParser(pydantic_object=MedicineInfo)

@app.get("/")
async def root():
    return {"message": "Medicine Information Extractor API"}

@app.post("/api/analyze-medicine", response_model=MedicineResponse)
async def analyze_medicine(file: UploadFile = File(...)):
    try:
        # Read image file
        image_data = await file.read()
        
        # Use Gemini Vision API to extract text from image
        # Try gemini-1.5-pro first, fallback to gemini-1.5-flash
        try:
            model_vision = genai.GenerativeModel('gemini-2.5-flash')
        except:
            model_vision = genai.GenerativeModel('gemini-2.0-flash')
        
        # Extract text from image
        prompt_extract = """
        Analyze this medicine image (strip, bottle, or package) extremely thoroughly. Extract ALL visible text, numbers, and symbols.
        Pay close attention to:
        - Brand name and generic name
        - Composition/ingredients with exact amounts (mg, ml, %)
        - Dosage instructions, frequency, and route of administration
        - Manufacturer details
        - Warnings, cautions, and storage instructions
        - Batch numbers and expiry dates
        
        Provide the extracted text in a structured format, distinguishing between main labels and fine print.
        """
        
        # For Gemini Vision, we need to pass the image directly
        import PIL.Image
        image = PIL.Image.open(io.BytesIO(image_data))
        
        # Convert image to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        response_vision = model_vision.generate_content([
            prompt_extract,
            image
        ])
        
        extracted_text = response_vision.text
        
        # Now use LangChain to extract structured medicine information
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a highly experienced clinical pharmacist and medical information expert. Your task is to analyze extracted text from medicine packaging and provide an extremely detailed and comprehensive profile of the medication.

            {format_instructions}
            
            Based ONLY on the provided text and your medical knowledge, generate a detailed report.
            
            GUIDELINES FOR DETAIL:
            - **Medicine Name**: Include specific strength (e.g., "Dolo 650mg") not just brand name.
            - **Ingredients**: List each ingredient with its exact quantity if available.
            - **Uses**: valid medical indications. Be specific.
            - **Dosage**: Provide standard dosage guidelines for adults and children if not explicitly stated, but clearly mark them as "standard guidelines" vs "specific instructions found".
            - **Warnings**: Include critical contraindications (pregnancy, liver/kidney issues, alcohol interaction).
            - **Side Effects**: List common and serious side effects.
            - **Storage**: specific temperature ranges if known.
            
            Do not hallucinate information, but use your medical knowledge to supplement missing context where safe (e.g., interpreting "Paracetamol" uses if only the name is visible)."""),
            ("human", "Extracted text from medicine label:\n\n{extracted_text}\n\nProvide the most detailed structured information possible about this medicine.")
        ])
        
        # Format the prompt with output parser instructions
        format_instructions = parser.get_format_instructions()
        messages = prompt_template.format_messages(
            extracted_text=extracted_text,
            format_instructions=format_instructions
        )
        
        # Get structured response
        response = llm.invoke(messages)
        
        # Parse the response
        try:
            # Extract JSON from response
            response_text = response.content
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                medicine_data = json.loads(json_str)
                medicine_info = MedicineInfo(**medicine_data)
            else:
                # Fallback: try to parse directly
                medicine_info = parser.parse(response_text)
        except Exception as e:
            # Fallback: create a basic structure
            medicine_info = MedicineInfo(
                medicine_name="Unable to parse",
                active_ingredients=["Information extraction in progress"],
                uses=["Analysis required"],
                side_effects=["Please check with healthcare provider"],
                age_recommendation="Consult healthcare provider",
                dosage="As prescribed by doctor"
            )
        
        return MedicineResponse(
            extracted_text=extracted_text,
            medicine_info=medicine_info
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Construct chat history for Gemini
        chat_history = []
        for msg in request.history:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})
        
        # Initialize chat with history
        chat = genai.GenerativeModel('gemini-2.5-flash').start_chat(history=chat_history)
        
        # System instruction is not directly supported in start_chat for all versions, 
        # so we prepend it to the first message or handle it via system instruction if supported.
        # ideally we should use system instruction if available, but for simplicity/compatibility:
        system_prompt = """You are a helpful and knowledgeable medical AI assistant. 
        Your goal is to provide accurate, safe, and helpful information about medicines, health conditions, and general medical queries.
        
        Guidelines:
        - Always advise users to consult a healthcare professional for specific medical advice, diagnosis, or treatment.
        - Be concise, professional, and empathetic.
        - If you are unsure, admit it and suggest seeking professional help.
        - Do not provide prescriptions or definitive diagnoses.
        - **FORMATTING**: Use Markdown to make your responses clear and readable. Use bolding for key terms, bullet points for lists, and headers for sections.
        """
        
        # Send message
        response = chat.send_message(f"{system_prompt}\n\nUser Question: {request.message}")
        
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.post("/api/check-interactions", response_model=InteractionResponse)
async def check_interactions(request: InteractionRequest):
    try:
        if len(request.medicines) < 2:
            raise HTTPException(status_code=400, detail="At least two medicines are required for interaction check.")

        # Prepare prompt for interaction check
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a highly experienced clinical pharmacist and drug-drug interaction expert. 
            Your task is to analyze a list of medicines and identify any potential interactions between them.
            
            {format_instructions}
            
            GUIDELINES:
            - Analyze EACH pair of medicines if more than two are provided.
            - **Overall Status**: Set to 'Dangerous' if any interaction is dangerous, 'Caution' if any is caution, otherwise 'Safe'.
            - **Severity**: Must be exactly 'Safe', 'Caution', or 'Dangerous'.
            - **Disclaimer**: Always include a standard medical disclaimer about consulting a physician.
            - If no interaction is found, return as 'Safe' with a brief explanation that no common interactions are known.
            - Be concise but thorough in explanations.
            """),
            ("human", "Check interactions for the following medicines: {medicines_list}")
        ])
        
        format_instructions = interaction_parser.get_format_instructions()
        medicines_list = ", ".join(request.medicines)
        
        messages = prompt_template.format_messages(
            medicines_list=medicines_list,
            format_instructions=format_instructions
        )
        
        # Get structured response from Gemini
        response = llm.invoke(messages)
        
        # Parse the response
        try:
            # Extract JSON from response
            response_text = response.content
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                interaction_data = json.loads(json_str)
                # Ensure it matches InteractionResponse
                return InteractionResponse(**interaction_data)
            else:
                return interaction_parser.parse(response_text)
        except Exception as e:
            # Fallback response
            return InteractionResponse(
                overall_status="Unknown",
                interactions=[InteractionDetail(
                    severity="Caution",
                    explanation=f"Error analyzing interactions: {str(e)}",
                    advice="Please consult a healthcare professional."
                )],
                disclaimer="Disclaimer: This AI analysis may be incomplete. Always consult with a doctor or pharmacist."
            )
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error checking interactions: {str(e)}")

@app.post("/api/generate-pdf")
async def generate_pdf(data: dict):
    try:
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#34495e',
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        elements.append(Paragraph("Medicine Information Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Medicine Name
        medicine_name = data.get('medicine_info', {}).get('medicine_name', 'N/A')
        elements.append(Paragraph(f"<b>Medicine Name:</b> {medicine_name}", heading_style))
        elements.append(Spacer(1, 0.1*inch))
        
        # Active Ingredients
        ingredients = data.get('medicine_info', {}).get('active_ingredients', [])
        if ingredients:
            elements.append(Paragraph("<b>Active Ingredients:</b>", styles['Heading3']))
            for ing in ingredients:
                elements.append(Paragraph(f"• {ing}", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Uses
        uses = data.get('medicine_info', {}).get('uses', [])
        if uses:
            elements.append(Paragraph("<b>Medical Uses:</b>", styles['Heading3']))
            for use in uses:
                elements.append(Paragraph(f"• {use}", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Side Effects
        side_effects = data.get('medicine_info', {}).get('side_effects', [])
        if side_effects:
            elements.append(Paragraph("<b>Side Effects:</b>", styles['Heading3']))
            for effect in side_effects:
                elements.append(Paragraph(f"• {effect}", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Age Recommendation
        age_rec = data.get('medicine_info', {}).get('age_recommendation', 'N/A')
        elements.append(Paragraph(f"<b>Age Recommendation:</b> {age_rec}", styles['Heading3']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Dosage
        dosage = data.get('medicine_info', {}).get('dosage', 'N/A')
        elements.append(Paragraph(f"<b>Dosage:</b> {dosage}", styles['Heading3']))
        elements.append(Spacer(1, 0.15*inch))
        
        # Warnings
        warnings = data.get('medicine_info', {}).get('warnings', [])
        if warnings:
            elements.append(Paragraph("<b>Warnings & Precautions:</b>", styles['Heading3']))
            for warning in warnings:
                elements.append(Paragraph(f"⚠ {warning}", styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Storage
        storage = data.get('medicine_info', {}).get('storage', '')
        if storage:
            elements.append(Paragraph(f"<b>Storage Instructions:</b> {storage}", styles['Heading3']))
            elements.append(Spacer(1, 0.15*inch))
        
        # Extracted Text
        extracted_text = data.get('extracted_text', '')
        if extracted_text:
            elements.append(PageBreak())
            elements.append(Paragraph("<b>Extracted Text from Image:</b>", heading_style))
            elements.append(Spacer(1, 0.1*inch))
            # Split long text into paragraphs
            text_paragraphs = extracted_text.split('\n')
            for para in text_paragraphs[:20]:  # Limit to first 20 lines
                if para.strip():
                    elements.append(Paragraph(para.strip(), styles['Normal']))
                    elements.append(Spacer(1, 0.05*inch))
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        buffer.seek(0)
        pdf_bytes = buffer.read()
        buffer.close()
        
        # Save to temporary file
        filename = f"medicine_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = f"/tmp/{filename}"
        
        # For Windows, use temp directory
        import tempfile
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(pdf_bytes)
        
        return FileResponse(
            filepath,
            media_type='application/pdf',
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

