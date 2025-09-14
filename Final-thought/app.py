import os, re, io
from flask import Flask, request, jsonify, render_template, send_file
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

LABEL_MAP = {0:"negative", 1:"positive", 2:"spam"}

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

def process_files(files):
    all_data = []
    for file in files:
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

        all_data.append(df[["clean_comment", "sentiment", "category"]])
    result_df = pd.concat(all_data, ignore_index=True)
    return result_df

# -------------------------
# ROUTES
# -------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({"error":"No file uploaded"}), 400
    files = request.files.getlist('files')
    try:
        df = process_files(files)
        df_json = df.to_dict(orient="records")
        # Save CSV to a BytesIO for download
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return jsonify({"data": df_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['POST'])
def download():
    files = request.files.getlist('files')
    df = process_files(files)
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return send_file(csv_buffer, mimetype="text/csv", as_attachment=True, download_name="labeled_comments.csv")

if __name__ == "__main__":
    app.run(debug=True)
