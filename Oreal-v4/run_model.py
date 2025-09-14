import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
from tqdm import tqdm

# -------------------------
# CONFIG
# -------------------------
MODEL_PATH = r"/mnt/c/Users/EBuddyHub/Desktop/Final-Thought/Model"  # WSL/Linux path
INPUT_CSV = r"/mnt/c/Users/EBuddyHub/Desktop/Final-Thought/split_3.csv"
OUTPUT_CSV = r"/mnt/c/Users/EBuddyHub/Desktop/Final-Thought/output_comments.csv"
COMMENT_COLUMN = "textOriginal"  # column containing raw YouTube comments
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
BATCH_SIZE = 64  # Adjust depending on GPU/CPU memory

# Map numeric labels to human-readable strings
LABEL_MAP = {
    0: "negative",
    1: "positive",
    2: "spam"
}

# -------------------------
# LOAD MODEL
# -------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(DEVICE)
model.eval()

# -------------------------
# DATA CLEANING FUNCTION
# -------------------------
def clean_comment(text):
    text = str(text).lower()  # lowercase
    text = re.sub(r"http\S+", "", text)  # remove URLs
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove special characters
    text = re.sub(r"\s+", " ", text).strip()  # remove extra spaces
    return text

# -------------------------
# DATA LOADING
# -------------------------
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()  # remove extra spaces in column names
df["clean_comment"] = df[COMMENT_COLUMN].apply(clean_comment)

# -------------------------
# PREDICTION FUNCTION (BATCH)
# -------------------------
def predict_batch(comments):
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True).to(DEVICE)
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

# Map numeric labels to human-readable labels
df["label"] = [LABEL_MAP.get(l, "unknown") for l in all_labels]

# -------------------------
# SAVE OUTPUT
# -------------------------
df.to_csv(OUTPUT_CSV, index=False)
print(f"Predictions saved to {OUTPUT_CSV}")
