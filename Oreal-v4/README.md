# YouTube Comments Analyzer

A web app to help you analyze YouTube comments quickly. Upload your CSV files and see which comments are positive, negative, or spam. You can also see what kind of topics people are talking about (like skincare, cosmetics, hair) and download a labeled CSV.

---

## Features

- Upload multiple CSV files with YouTube comments.
- Automatically detect sentiment:
  - Positive 👍
  - Negative 👎
  - Spam 🚫
- Categorize comments by topic:
  - Skincare
  - Cosmetics
  - Hair
  - General
- Interactive charts showing sentiment and category distribution.
- Filter comments to see only positive or negative ones.
- Download your comments with sentiment and category added.

---

## How It Looks

- **Dashboard**: View overall charts for sentiment and categories.  
- **Positive & Negative Tabs**: See comments and filter by category.  
- **Download Button**: Save all labeled comments as a CSV file.  

---

## How to Use

1. Open the app in your browser (after running the server).  
2. Upload one or more CSV files with a column called `textOriginal`.  
3. Wait a few seconds for the analysis to complete.  
4. Explore charts and filtered comments.  
5. Click **Download Labeled CSV** to save the results.

---

## File Requirements

- Must be a **CSV file**.  
- Must have a column called `textOriginal` with the comment text.

Example:

| textOriginal                     |
|----------------------------------|
| I love this product!             |
| This is terrible quality.        |
| Amazing skincare routine!        |

---

## Technology Used

- **Frontend**: Looks nice and interactive using **Bootstrap** and **Chart.js**.  
- **Backend**: Processes your comments using Python and a machine learning model.  

---

## Notes

- Large files may take a few seconds to analyze.  
- Works best if your CSV column is named exactly `textOriginal`.

---

## Download

Click **Download Labeled CSV** after the analysis is done to save your comments with sentiment and category.
