import os
import re
import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import emoji

# -------------------------
# CONFIG
# -------------------------
INPUT_CSV = r"C:\Users\lmk\Desktop\oreal-datathon\Oreal-v4\split_3.csv"
OUTPUT_CSV = r"C:\Users\lmk\Desktop\oreal-datathon\Oreal-v4\output_labeled.csv"
SIMPLIFIED_CSV = r"C:\Users\lmk\Desktop\oreal-datathon\Oreal-v4\output_simplified.csv"
COMMENT_COLUMN = "textOriginal"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 64

# Sentiment mapping for model
LABEL_MAP = {0: "negative", 1: "positive", 2: "spam"}

# Beauty keywords
BEAUTY_KEYWORDS = {
    "skincare": ["skin", "cream", "lotion", "serum", "mask", "moisturizer", "spf"],
    "cosmetic": ["makeup", "foundation", "lipstick", "eyeliner", "blush", "eyeshadow"],
    "hair": ["shampoo", "conditioner", "hair", "styling", "haircare"],
}

# General command keywords
COMMAND_KEYWORDS = ["subscribe", "follow", "like", "share", "comment", "click"]

# Positive/negative emoji lists
POSITIVE_EMOJIS = ["😊", "😍", "👍", "💖", "🥰"]
NEGATIVE_EMOJIS = ["😡", "😢", "👎", "💔", "😞", "🤮", "💩"]

# -------------------------
# LOAD MODEL
# -------------------------
MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment"
print(f"Loading model {MODEL_NAME} on {DEVICE}...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.to(DEVICE)
model.eval()
print("Model loaded successfully.")

# -------------------------
# CLEAN COMMENTS (keep emojis)
# -------------------------
def clean_comment(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)  # remove URLs
    # keep letters, numbers, spaces, emojis
    allowed = []
    for char in text:
        if char.isalnum() or char.isspace() or emoji.is_emoji(char):
            allowed.append(char)
    text = "".join(allowed)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------
# EMOJI SENTIMENT
# -------------------------
def adjust_sentiment_with_emoji(text, sentiment):
    for e in POSITIVE_EMOJIS:
        if e in text:
            return "positive"
    for e in NEGATIVE_EMOJIS:
        if e in text:
            return "negative"
    return sentiment

# -------------------------
# CATEGORY DETECTION
# -------------------------
def detect_category(text):
    text_lower = str(text).lower()
    for cat, keywords in BEAUTY_KEYWORDS.items():
        for word in keywords:
            if word in text_lower:
                return cat
    for cmd in COMMAND_KEYWORDS:
        if cmd in text_lower:
            return "general_command"
    return "other"

# -------------------------
# PREDICTION FUNCTION
# -------------------------
def predict_batch(comments):
    inputs = tokenizer(
        comments,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=256
    ).to(DEVICE)
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        labels = torch.argmax(probs, dim=-1)
    return labels.cpu().numpy()

# -------------------------
# LOAD CSV
# -------------------------
print(f"Loading CSV from {INPUT_CSV}...")
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()
df["clean_comment"] = df[COMMENT_COLUMN].apply(clean_comment)
print(f"Loaded {len(df)} comments.")

# -------------------------
# RUN SENTIMENT MODEL
# -------------------------
all_labels = []
print("Running sentiment predictions...")
for i in tqdm(range(0, len(df), BATCH_SIZE)):
    batch_comments = df["clean_comment"].iloc[i:i+BATCH_SIZE].tolist()
    labels = predict_batch(batch_comments)
    all_labels.extend(labels)

df["sentiment"] = [LABEL_MAP.get(l, "unknown") for l in all_labels]

# -------------------------
# ADJUST SENTIMENT WITH EMOJI
# -------------------------
df["sentiment"] = df.apply(lambda row: adjust_sentiment_with_emoji(row["clean_comment"], row["sentiment"]), axis=1)

# -------------------------
# DETECT CATEGORY
# -------------------------
df["category"] = df["clean_comment"].apply(detect_category)

# -------------------------
# SAVE OUTPUT
# -------------------------
df.to_csv(OUTPUT_CSV, index=False)
print(f"Full output saved to {OUTPUT_CSV}")

# Simplified CSV for HTML analyzer
df_simplified = df[['clean_comment', 'sentiment', 'category']]
df_simplified.to_csv(SIMPLIFIED_CSV, index=False)
print(f"Simplified CSV saved to {SIMPLIFIED_CSV}")
