# app/main.py
import io
import img2pdf
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from src.process_document import process_document

app = FastAPI(title="CamScanner Clone API", version="0.7.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return {"message": "Welcome to the CamScanner Clone API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/scan-document")
async def scan_document_endpoint(
    file: UploadFile = File(..., description="Image file to scan"),
    mode: str = Query(
        default="scan",description="Processing mode: original, color, gray, scan, enhanced"
    ),
):
    try:
        contents = await file.read()
        processed_bytes = process_document(contents, mode)
        return StreamingResponse(
            io.BytesIO(processed_bytes),
            media_type="image/jpeg"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scan-to-pdf")
async def scan_to_pdf_endpoint(
    files: List[UploadFile] = File(..., description="Multiple image files"),
    mode: str = Query(
        default="scan",
        description="Processing mode: original, color, gray, scan, enhanced",
    ),
):
    """
    Upload an image of a document to get a flattened, top-down scanned version.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    try:
        processed_images = []

        for file in files:
            contents = await file.read()
            processed_bytes = process_document(contents, mode)
            # Wrap the bytes in BytesIO so img2pdf can read it like a file
            processed_images.append(io.BytesIO(processed_bytes))

        # convert list of images to a pdf
        pdf_bytes = img2pdf.convert(processed_images)

        # return PDF as downloadable
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=scanned_document.pdf"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
