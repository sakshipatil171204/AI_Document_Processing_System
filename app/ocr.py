
from paddleocr import PaddleOCR
import os
import sys
import json
from pdf2image import convert_from_path


# Create OCR object
ocr = PaddleOCR(
    lang="en"
)


# Get file path from command line
if len(sys.argv) < 2:
    print("Please provide an image or PDF path.")
    print("Example: python app/ocr.py dataset/invoice/invoice01.png")
    print("Example: python app/ocr.py dataset/invoice/invoice01.pdf")
    sys.exit(1)


file_path = sys.argv[1]


# Check if file exists
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)


# Folder where OCR text will be saved
output_folder = "data/ocr_text"
os.makedirs(output_folder, exist_ok=True)


# Get file extension
file_extension = os.path.splitext(file_path)[1].lower()


# Store all extracted text
all_text = []


# ---------------------------------------------------
# IMAGE FILES
# ---------------------------------------------------

if file_extension in [".jpg", ".jpeg", ".png"]:

    result = ocr.predict(file_path)

    for res in result:

        # Get JSON result
        data = res.json

        if isinstance(data, str):
            data = json.loads(data)

        # PaddleOCR 3.x stores the result inside "res"
        if "res" in data:
            data = data["res"]

        # Get recognized text
        if "rec_texts" in data:
            all_text.extend(data["rec_texts"])


# ---------------------------------------------------
# PDF FILE
# ---------------------------------------------------

elif file_extension == ".pdf":

    print("PDF detected. Converting PDF pages to images...")

    # Convert PDF pages to images
    pages = convert_from_path(file_path)

    print(f"Number of PDF pages: {len(pages)}")

    # Run OCR on each page
    for page_number, page in enumerate(pages, start=1):

        print(f"Processing PDF page {page_number}...")

        # Temporary image for the current page
        temp_image = f"temp_page_{page_number}.png"

        # Save page as image
        page.save(temp_image)

        # Run OCR
        result = ocr.predict(temp_image)

        for res in result:

            # Get JSON result
            data = res.json

            if isinstance(data, str):
                data = json.loads(data)

            # PaddleOCR 3.x stores the result inside "res"
            if "res" in data:
                data = data["res"]

            # Get recognized text
            if "rec_texts" in data:
                all_text.extend(data["rec_texts"])

        # Delete temporary image
        if os.path.exists(temp_image):
            os.remove(temp_image)


# ---------------------------------------------------
# UNSUPPORTED FILE
# ---------------------------------------------------

else:

    print("Unsupported file type.")
    print("Supported formats: JPG, JPEG, PNG, PDF")
    sys.exit(1)


# ---------------------------------------------------
# CREATE OUTPUT FILE
# ---------------------------------------------------

filename = os.path.splitext(
    os.path.basename(file_path)
)[0]


output_file = os.path.join(
    output_folder,
    filename + ".txt"
)


# ---------------------------------------------------
# SAVE EXTRACTED TEXT
# ---------------------------------------------------

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    for text in all_text:
        file.write(text + "\n")


# ---------------------------------------------------
# FINAL MESSAGE
# ---------------------------------------------------

print("OCR completed successfully!")
print(f"Text saved to: {output_file}")
print(f"Number of text lines extracted: {len(all_text)}")
