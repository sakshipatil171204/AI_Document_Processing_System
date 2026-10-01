from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import shutil


from app.ocr import extract_text
from app.classifier import classify_document

from app.extractor import (
    extract_invoice_details,
    extract_resume_details,
    extract_marksheet_details,
    extract_resume_skills,
    extract_subject_marks
)
from app.validator import (
    validate_invoice,
    validate_resume,
    validate_marksheet
)
app = FastAPI(
    title="AI Document Processing System"
)


templates = Jinja2Templates(
    directory="templates"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.post("/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...)
):

    allowed_extensions = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png"
    }

    filename = file.filename

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension not in allowed_extensions:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Only PDF, JPG, JPEG and PNG files are allowed."
            }
        )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # -----------------------------
    # OCR
    # -----------------------------

    try:

        extracted_text = extract_text(
            file_path
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"OCR failed: {str(e)}"
            }
        )

    # -----------------------------
    # ML CLASSIFICATION
    # -----------------------------

    try:

        document_type = classify_document(
            extracted_text
        )

        print("DEBUG DOCUMENT TYPE:", document_type)

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Classification failed: {str(e)}"
            }
        )

    # -----------------------------
    # INFORMATION EXTRACTION
    # -----------------------------

    extracted_details = {}

    try:

        if document_type.lower() == "invoice":

            extracted_details = extract_invoice_details(
                extracted_text
            )

        elif document_type.lower() == "resume":

            extracted_details = extract_resume_details(
                extracted_text
            )

            extracted_details["skills"] = extract_resume_skills(
                extracted_text
            )

        elif document_type.lower() == "marksheet":

            extracted_details = extract_marksheet_details(
                extracted_text
            )

            extracted_details["subject_marks"] = extract_subject_marks(
                extracted_text
            )

        print(
            "DEBUG EXTRACTED DETAILS:",
            extracted_details
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Information extraction failed: {str(e)}"
            }
        )

    # -----------------------------
    # VALIDATION
    # -----------------------------

    validation_result = {}

    try:

        if document_type.lower() == "invoice":

            validation_result = validate_invoice(
                extracted_details
            )

        elif document_type.lower() == "resume":

            validation_result = validate_resume(
                extracted_details
            )

        elif document_type.lower() == "marksheet":

            validation_result = validate_marksheet(
                extracted_details
            )

        print(
            "DEBUG VALIDATION RESULT:",
            validation_result
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Validation failed: {str(e)}"
            }
        )

    # -----------------------------
    # DISPLAY RESULT
    # -----------------------------

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "message": f"{filename} processed successfully!",
            "document_type": document_type,
            "extracted_text": extracted_text,
            "extracted_details": extracted_details,
            "validation_result": validation_result
        }
    )