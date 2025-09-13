import streamlit as st
import pandas as pd
import google.generativeai as genai

# ------------------------------
# Setup Gemini
# ------------------------------
# Put your Gemini API key in Streamlit secrets or replace with string
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

def classify_relevance(comments, selected_topic):
    """
    Use Gemini to classify comments as Relevant/Not Relevant to the selected_topic.
    Processes in batch for efficiency.
    """
    prompt = f"""
    You are a helpful assistant. 
    For each of the following comments, decide if it is relevant to the topic "{selected_topic}".
    Reply in JSON format as a list of objects with this structure:
    [{{"comment": "...", "relevance": "Relevant/Not Relevant"}}]

    Comments:
    {comments}
    """

    response = model.generate_content(prompt)
    return response.text


# ------------------------------
# Streamlit UI
# ------------------------------
st.title("YouTube Comment Relevance Classifier (Gemini)")

# 1. Upload CSV
uploaded_file = st.file_uploader("Upload your comments CSV", type="csv")

# 2. Topic selection
selected_topic = st.selectbox(
    "Choose a topic:",
    ["makeup", "skincare", "fragrance"]
)

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Normalize column names
    if "textOriginal" in df.columns and "likeCount" in df.columns:
        df = df.rename(columns={"textOriginal": "comment", "likeCount": "likes"})

    # Drop missing
    df = df.dropna(subset=["comment"])

    st.write("### Raw Data", df.head())

    # 3. Run Gemini classification
    if st.button("Classify Relevance with Gemini"):
        # Process in small batches (Gemini input limit)
        batch_size = 10
        results = []

        for i in range(0, len(df), batch_size):
            batch = df["comment"].iloc[i:i+batch_size].tolist()
            gemini_result = classify_relevance(batch, selected_topic)

            # Try to parse JSON safely
            try:
                batch_results = pd.read_json(gemini_result)
                results.append(batch_results)
            except Exception as e:
                st.error(f"Failed to parse Gemini output: {e}")
                st.text(gemini_result)

        if results:
            relevance_df = pd.concat(results, ignore_index=True)

            # Merge relevance back into original df
            processed = df.merge(relevance_df, on="comment", how="left")

            st.write("### Processed Data", processed.head())

            # 4. Show Relevance Ratio
            st.subheader("Relevance Ratio")
            st.bar_chart(processed["relevance"].value_counts())

            # Save processed results
            st.download_button(
                "Download Processed CSV",
                data=processed.to_csv(index=False).encode("utf-8"),
                file_name="processed_comments.csv",
                mime="text/csv"
            )
