import pandas as pd
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

analyzer = SentimentIntensityAnalyzer()

# 1. Cleaning
def clean_comment(comment):
    # Handle missing or non-string inputs
    if not isinstance(comment, str):
        comment = ""
    
    # Create TextBlob safely
    blob = TextBlob(comment if comment.strip() != "" else "neutral")
    
    # Detect language (fallback = English)
    try:
        lang = blob.detect_language()
    except:
        lang = "en"
    
    # Translate if not English (skip if empty)
    if lang != "en" and comment.strip() != "":
        try:
            comment = str(blob.translate(to="en"))
        except:
            pass
    
    # Simple spam detection with regex
    spam_patterns = [r"subscribe", r"giveaway", r"http", r"https"]
    is_spam = any(re.search(pattern, comment.lower()) for pattern in spam_patterns)
    
    return comment, is_spam

# 2. Topic Extraction
def extract_topic(comment):
    topics = {
        "makeup technique": ["makeup", "blend", "foundation", "lipstick", "eyeshadow"],
        "general feedback": ["love", "great", "amazing", "awesome"],
        "editing": ["edit", "cut", "transition", "subtitle"],
        "spam": ["subscribe", "giveaway", "link", "channel"]
    }
    for topic, keywords in topics.items():
        if any(word in comment.lower() for word in keywords):
            return topic
    return "general"

# 3. Sentiment
def get_sentiment(comment):
    scores = analyzer.polarity_scores(comment)
    compound = scores["compound"]
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    else:
        return "neutral"

# 4. Engagement
def get_engagement(comment):
    if "?" in comment:
        return "question"
    elif re.search(r"(thanks|love|great|amazing)", comment.lower()):
        return "praise"
    elif re.search(r"(should|could|maybe|try)", comment.lower()):
        return "suggestion"
    elif re.search(r"(stupid|hate|terrible|awful)", comment.lower()):
        return "harassment"
    else:
        return "general"

# Main Pipeline
def process_comments(df):
    results = []
    for _, row in df.iterrows():
        comment = row.get("comment", "")
        likes = row.get("likes", 0)
        
        cleaned, is_spam = clean_comment(comment)
        topic = "spam" if is_spam else extract_topic(cleaned)
        sentiment = "spam" if is_spam else get_sentiment(cleaned)
        engagement = "spam" if is_spam else get_engagement(cleaned)
        
        results.append({
            "comment": cleaned,
            "likes": likes,
            "spam": is_spam,
            "topic": topic,
            "sentiment": sentiment,
            "engagement": engagement
        })
    
    return pd.DataFrame(results)
