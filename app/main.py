from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import shutil

from app.ocr import extract_text
from app.classifier import classify_document


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
    # DISPLAY RESULT
    # -----------------------------

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "message": f"{filename} processed successfully!",
            "document_type": document_type,
            "extracted_text": extracted_text
        }
    )