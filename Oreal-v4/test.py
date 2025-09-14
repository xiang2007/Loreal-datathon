import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
from tqdm import tqdm

# -------------------------
# CONFIG
# -------------------------
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
INPUT_CSV = r"/mnt/c/Users/EBuddyHub/Desktop/Final-Thought/split_1.csv"
OUTPUT_CSV = r"/mnt/c/Users/EBuddyHub/Desktop/Final-Thought/output_comments.csv"
COMMENT_COLUMN = "textOriginal"  # column containing raw YouTube comments
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 256  # increase for GPU

# Sentiment labels of the model
LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}

# -------------------------
# LOAD MODEL
# -------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()

# -------------------------
# DATA CLEANING FUNCTION
# -------------------------
def clean_comment(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove special chars
    text = re.sub(r"\s+", " ", text).strip()  # remove extra spaces
    return text

# -------------------------
# DATA LOADING
# -------------------------
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()
df["clean_comment"] = df[COMMENT_COLUMN].apply(clean_comment)

# -------------------------
# PREDICTION FUNCTION (BATCH)
# -------------------------
def predict_batch(comments):
    # Tokenize on CPU, then move tensors to GPU
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True)
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = torch.argmax(probs, dim=-1)
    return labels.cpu().numpy()

# -------------------------
# RUN MODEL IN BATCHES
# -------------------------
all_labels = []

for i in tqdm(range(0, len(df), BATCH_SIZE)):
    batch_comments = df["clean_comment"].iloc[i:i+BATCH_SIZE].tolist()
    labels = predict_batch(batch_comments)
    all_labels.extend(labels)

# Map numeric labels to human-readable strings
df["label"] = [LABEL_MAP.get(l, "unknown") for l in all_labels]

# -------------------------
# SAVE OUTPUT
# -------------------------
df.to_csv(OUTPUT_CSV, index=False)
print(f"Predictions saved to {OUTPUT_CSV}")
