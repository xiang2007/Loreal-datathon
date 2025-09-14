# YouTube Comments Analyzer

Enterprise-style web application to analyze YouTube comments in CSV files.  
It classifies comments by **sentiment** and **category**, provides interactive charts, and allows downloading the labeled CSV.

---

## Features

- Upload multiple CSV files at once
- Clean and process comments
- Classify comments into:
  - **Sentiment:** positive, negative, spam
  - **Category:** skincare, cosmetic, hair, general
- Interactive charts for:
  - Sentiment distribution
  - Category distribution
- Filter comments by category
- Download labeled CSV

---

## Requirements

- Python 3.9+
- pip packages:
  - Flask
  - pandas
  - torch
  - transformers
  - tqdm

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/oreal-datathon.git
cd oreal-datathon

2. Create a virtual environment:

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

3. Install dependencies:

pip install -r requirements.txt

4. Usage

Start the Flask server:

python app.py

Open your browser and go to:

http://127.0.0.1:5000/

Upload CSV files with a column named textOriginal.

View the Dashboard, Positive, and Negative tabs.

Filter comments by category.

Download the labeled CSV using the Download Labeled CSV button.