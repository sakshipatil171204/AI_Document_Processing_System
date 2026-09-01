from paddleocr import PaddleOCR
import os
import sys
import json


# Create OCR object
ocr = PaddleOCR(
    lang="en"
)


# Get image path from command line
if len(sys.argv) < 2:
    print("Please provide an image path.")
    print("Example: python app/ocr.py dataset/invoice/invoice01.png")
    sys.exit(1)

image_path = sys.argv[1]


# Check if image exists
if not os.path.exists(image_path):
    print(f"Image not found: {image_path}")
    sys.exit(1)


# Folder where OCR text will be saved
output_folder = "data/ocr_text"
os.makedirs(output_folder, exist_ok=True)


# Run OCR
result = ocr.predict(image_path)


# Extract recognized text
all_text = []

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
print(f"Number of text lines extracted: {len(all_text)}")