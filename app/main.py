from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import os
import shutil


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
            "index.html",
            {
                "request": request,
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


    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={
        "message": f"{filename} uploaded successfully!"
    }
)