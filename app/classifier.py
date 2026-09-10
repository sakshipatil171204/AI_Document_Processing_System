import joblib
import os

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths to saved model and vectorizer
MODEL_PATH = os.path.join(BASE_DIR, "models", "document_classifier.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl")

# Load trained model and TF-IDF vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def classify_document(text):
    """
    Classifies OCR-extracted text into:
    Invoice, Marksheet, or Resume.
    """

    # Convert text into TF-IDF features
    text_vector = vectorizer.transform([text])

    # Predict document type
    prediction = model.predict(text_vector)

    return prediction[0]