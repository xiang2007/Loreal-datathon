import os, re, io
from flask import Flask, request, jsonify, render_template
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from tqdm import tqdm

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
COMMENT_COLUMN = "textOriginal"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 64

LABEL_MAP = {
    0: "negative",
    1: "positive",
    2: "spam"
}

CATEGORY_KEYWORDS = {
    "skincare": ["skin", "moisturizer", "serum", "lotion", "cream"],
    "cosmetic": ["lipstick", "makeup", "eyeliner", "foundation"],
    "hair": ["hair", "curly", "shampoo", "conditioner", "braid"]
}

# -------------------------
# LOAD MODEL
# -------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()

# -------------------------
# FUNCTIONS
# -------------------------
def clean_comment(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def categorize_comment(text):
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return cat
    return "general"

def predict_batch(comments):
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True, max_length=256).to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = torch.argmax(probs, dim=-1)
    return labels.cpu().numpy()

def process_csv(file):
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    df["clean_comment"] = df[COMMENT_COLUMN].apply(clean_comment)
    
    all_labels = []
    for i in tqdm(range(0, len(df), BATCH_SIZE)):
        batch = df["clean_comment"].iloc[i:i+BATCH_SIZE].tolist()
        labels = predict_batch(batch)
        all_labels.extend(labels)
    
    df["sentiment"] = [LABEL_MAP.get(l, "unknown") for l in all_labels]
    df["category"] = df["clean_comment"].apply(categorize_comment)
    # Only keep necessary columns for frontend
    return df[["clean_comment", "sentiment", "category"]].to_dict(orient="records")

# -------------------------
# ROUTES
# -------------------------
@app.route('/')
def index():
    return render_template("index.html")  # Use the HTML dashboard from earlier

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    try:
        result = process_csv(file)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
