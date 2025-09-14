# app.py
from flask import Flask, request, jsonify
import pandas as pd
import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = Flask(__name__)

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
COMMENT_COLUMN = "textOriginal"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load model once at startup
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()

LABEL_MAP = {0:"negative", 1:"positive", 2:"spam"}

# Example simple categories based on keywords
CATEGORY_KEYWORDS = {
    "skincare":["skin","moistur","cream"],
    "cosmetic":["makeup","lipstick","foundation"],
    "hair":["hair","curly","shampoo"],
}

def clean_comment(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def detect_category(text):
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return cat
    return "general"

def predict_batch(comments):
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True, max_length=256).to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = torch.argmax(probs, dim=-1)
    return labels.cpu().numpy()

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error":"No file uploaded"}), 400
    file = request.files['file']
    try:
        df = pd.read_csv(file)
        df["clean_comment"] = df[COMMENT_COLUMN].apply(clean_comment)
        labels = predict_batch(df["clean_comment"].tolist())
        df["sentiment"] = [LABEL_MAP[l] for l in labels]
        df["category"] = df["clean_comment"].apply(detect_category)

        # Convert to JSON array
        data = df[["clean_comment","sentiment","category"]].to_dict(orient="records")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__=="__main__":
    app.run(debug=True)
