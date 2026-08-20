from paddleocr import PaddleOCR
import os


# Create OCR object
ocr = PaddleOCR(
    lang="en"
)


# Image to process
image_path = "dataset/invoice/invoice01.png"


# Folder where OCR text will be saved
output_folder = "data/ocr_text"

os.makedirs(output_folder, exist_ok=True)


# Run OCR
result = ocr.predict(image_path)


# Extract recognized text
all_text = []

for res in result:
    if hasattr(res, "json"):
        data = res.json

        # Handle JSON data
        if isinstance(data, str):
            import json
            data = json.loads(data)

        if "rec_texts" in data:
            all_text.extend(data["rec_texts"])


# Create output filename
filename = os.path.splitext(
    os.path.basename(image_path)
)[0]

output_file = os.path.join(
    output_folder,
    filename + ".txt"
)


# Save extracted text
with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    for text in all_text:
        file.write(text + "\n")


print("OCR completed successfully!")
print(f"Text saved to: {output_file}")