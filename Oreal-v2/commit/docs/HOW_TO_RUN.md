# 🚀 How to Run L'Oréal Comment Analysis

## 📋 Quick Start Guide

### Method 1: Web Interface (Recommended for Beginners)
```bash
# Start the web app
streamlit run streamlit_app.py
```
Then open your browser to `http://localhost:8501`

### Method 2: One Command Processing (Best for Multiple Files)
```bash
# Process all CSV files in current directory
python one_command.py

# Process files in specific folder
python one_command.py your_data_folder/
```

### Method 3: Windows Users (Double-Click)
- For web app: Double-click `run_app.bat`
- For batch processing: Put files in `batch_input/` folder, then double-click `run_batch.bat`

### Method 4: Traditional Command Line
```bash
# Process single dataset
python main.py

# Batch process multiple files
python batch_processor.py
```

## 📁 File Preparation

### Your CSV Files Need:
**Comments File:**
- `videoId` column (required)
- `textOriginal` column (required)
- `likeCount` column (optional)
- `replyCount` column (optional)
- `publishedAt` column (optional)

**Videos File:**
- `videoId` column (required)
- `title` column (required)
- `description` column (optional)

## 🎯 Choose Your Method

### For Single Dataset:
1. **Web Interface**: Upload 2 files, click analyze
2. **Command Line**: Put files in `data/` folder, run `python main.py`

### For Multiple Datasets:
1. **Web Interface**: Choose "Multiple Datasets" mode, upload all files
2. **One Command**: Put all files in folder, run `python one_command.py folder_name/`
3. **Batch Processor**: Put files in `batch_input/`, run `python batch_processor.py`

## 🔧 Installation Check
```bash
# Make sure you have all dependencies
python install_dependencies.py

# Or use the quick installer
python quick_install.py
```

## 📊 What You Get
- **CSV files** with full analysis results
- **Text reports** with insights and recommendations
- **Interactive visualizations** (web interface)
- **Summary statistics** across all datasets