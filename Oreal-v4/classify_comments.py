import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# -------- CONFIG --------
MODEL_PATH = "./comment_filter_model"  # change if your model folder is named differently
INPUT_FILE = "split_1.csv"      # your input CSV
OUTPUT_FILE = "labeled_comments.csv"   # output file
NUM_COMMENTS = 1000                   # number of comments to process
# ------------------------

# Label mapping
label_map = {
    "LABEL_0": "positive",
    "LABEL_1": "negative",
    "LABEL_2": "spam"
}

# Load model + tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

# Create pipeline
comment_filter = pipeline("text-classification", model=model, tokenizer=tokenizer)

# Read CSV
df = pd.read_csv(INPUT_FILE)

# If no "comment" column, take the first column as comment
if "comment" not in df.columns:
    first_col = df.columns[0]
    df = df[[first_col]].rename(columns={first_col: "comment"})

# Take only first N comments
subset_df = df.head(NUM_COMMENTS).copy()

# Run predictions
predictions = comment_filter(subset_df["comment"].astype(str).tolist(), truncation=True)

# Add results
subset_df["predicted_label"] = [label_map.get(p["label"], p["label"]) for p in predictions]
subset_df["confidence"] = [p["score"] for p in predictions]

# Save results
subset_df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Done! Saved {len(subset_df)} labeled comments to {OUTPUT_FILE}")
