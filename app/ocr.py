from paddleocr import PaddleOCR
import os
import json
from pdf2image import convert_from_path


# Create OCR object
ocr = PaddleOCR(lang="en")


def extract_text(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Project root directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Folder where OCR text will be saved
    output_folder = os.path.join(BASE_DIR, "data", "ocr_text")
    os.makedirs(output_folder, exist_ok=True)

    file_extension = os.path.splitext(file_path)[1].lower()

    all_text = []

    # -----------------------------
    # IMAGE FILES
    # -----------------------------
    if file_extension in [".jpg", ".jpeg", ".png"]:

        result = ocr.predict(file_path)

        for res in result:

            data = res.json

            if isinstance(data, str):
                data = json.loads(data)

            if "res" in data:
                data = data["res"]

            if "rec_texts" in data:
                all_text.extend(data["rec_texts"])

    # -----------------------------
    # PDF FILES
    # -----------------------------
    elif file_extension == ".pdf":

        print("PDF detected. Converting PDF pages to images...")

        pages = convert_from_path(file_path)

        print(f"Number of PDF pages: {len(pages)}")

        for page_number, page in enumerate(pages, start=1):

            print(f"Processing PDF page {page_number}...")

            temp_image = os.path.join(
                output_folder,
                f"temp_page_{page_number}.png"
            )

            page.save(temp_image)

            result = ocr.predict(temp_image)

            for res in result:

                data = res.json

                if isinstance(data, str):
                    data = json.loads(data)

                if "res" in data:
                    data = data["res"]

                if "rec_texts" in data:
                    all_text.extend(data["rec_texts"])

            # Delete temporary image
            if os.path.exists(temp_image):
                os.remove(temp_image)

    else:

        raise ValueError(
            "Unsupported file type. "
            "Supported formats: JPG, JPEG, PNG, PDF"
        )

    # Combine all extracted text
    extracted_text = "\n".join(all_text)

    # Create output TXT filename
    filename = os.path.splitext(
        os.path.basename(file_path)
    )[0]

    output_file = os.path.join(
        output_folder,
        filename + ".txt"
    )

    # Save OCR text
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(extracted_text)

    print("OCR completed successfully!")
    print(f"Text saved to: {output_file}")
    print(f"Number of text lines extracted: {len(all_text)}")

    return extracted_text