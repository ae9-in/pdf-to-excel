from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import base64
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from extraction import (
    extract_text_from_pdf,
    detect_pdf_type,
    ocr_pdf,
    extract_text_from_docx,
    extract_text_from_doc
)
from ai_parser import parse_tasks_with_llm
from excel_generator import generate_excel
from models import ConversionResult


app = FastAPI(title="EarlyBird PDF→Excel Service", version="1.0.0")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    """
    Main conversion endpoint.
    Accepts PDF, extracts data using LLM/OCR, generates formatted Excel, and returns results.
    """
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.docx') or filename_lower.endswith('.doc')):
        raise HTTPException(400, "Only PDF, DOCX, and DOC files are accepted")
    
    # Check file size (50MB limit)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(413, "File too large. Maximum size is 50MB")

    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ext = Path(file.filename).suffix.lower()
            input_path = Path(tmp_dir) / f"input{ext}"
            input_path.write_bytes(content)

            page_count = 1
            if ext == '.pdf':
                # Step 1: Detect PDF type
                pdf_type = detect_pdf_type(str(input_path))
                print(f"[DEBUG] Detected PDF type: {pdf_type}")

                # Step 2: Extract text
                if pdf_type == "text":
                    raw_text, page_count = extract_text_from_pdf(str(input_path))
                else:
                    raw_text, page_count = ocr_pdf(str(input_path))
                method = pdf_type
            elif ext == '.docx':
                print("[DEBUG] Processing DOCX file")
                raw_text, page_count = extract_text_from_docx(str(input_path))
                method = "docx"
            elif ext == '.doc':
                print("[DEBUG] Processing DOC file")
                raw_text, page_count = extract_text_from_doc(str(input_path))
                method = "doc"
            else:
                raise HTTPException(400, "Unsupported file extension")

            print(f"[DEBUG] Extracted text length: {len(raw_text)} chars. Page count: {page_count}")
            
            # Save raw text to workspace for debug
            try:
                debug_path = Path("d:/pdf to excal/extracted_debug.txt")
                debug_path.write_text(raw_text, encoding="utf-8")
                print(f"[DEBUG] Wrote raw text to {debug_path}")
            except Exception as de:
                print(f"[DEBUG] Failed to write debug file: {de}")

            print(f"[DEBUG] First 200 chars: {repr(raw_text[:200])}")

            if not raw_text.strip():
                raise HTTPException(422, "Could not extract any text from the document")

            # Step 3: LLM parsing (Claude API)
            result = await parse_tasks_with_llm(raw_text, page_count, method)

            # Step 4: Generate Excel
            xlsx_bytes = generate_excel(result)

            # Return response
            out_filename = file.filename.replace(ext, "_converted.xlsx")
            return {
                "success": True,
                "filename": out_filename,
                "xlsx_base64": base64.b64encode(xlsx_bytes).decode(),

                "summary": {
                    "task_count": len(result.tasks),
                    "sprint_title": result.sprint_title,
                    "organisation": result.organisation,
                    "method": result.method,
                    "confidence": result.confidence,
                    "page_count": page_count,
                },
                "result": result.model_dump(by_alias=True)
            }
    except ValueError as ve:
        # Anthropic key missing or validation error
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")


@app.post("/generate_excel")
async def generate_excel_endpoint(result: ConversionResult):
    """
    Accepts ConversionResult JSON (possibly edited by the user) and returns
    new base64-encoded styled Excel bytes.
    """
    try:
        xlsx_bytes = generate_excel(result)
        return {
            "success": True,
            "xlsx_base64": base64.b64encode(xlsx_bytes).decode()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Excel: {str(e)}")


@app.get("/health")
def health():
    return {"status": "ok", "tesseract": os.path.exists(os.environ.get("TESSERACT_PATH", ""))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
