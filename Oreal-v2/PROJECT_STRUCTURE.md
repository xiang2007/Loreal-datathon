# 📁 Project Structure

```
loreal-comment-analysis/
├── 📱 MAIN APPLICATION FILES
│   ├── streamlit_app.py          # Main Streamlit web application
│   ├── app.py                    # Entry point for deployment
│   ├── requirements.txt          # Python dependencies
│   └── Procfile                  # Deployment configuration
│
├── 🧠 CORE MODULES
│   └── src/
│       ├── data_processing.py    # Data loading and cleaning
│       ├── analysis.py           # Comment classification and analysis
│       └── dashboard.py          # Visualization and insights
│
├── ⚙️ CONFIGURATION
│   ├── config/
│   │   ├── analysis_config.py    # Analysis parameters
│   │   └── large_dataset_config.py # Large dataset optimizations
│   └── .streamlit/
│       └── config.toml           # Streamlit configuration
│
├── 🔧 SCRIPTS (Optional - for advanced users)
│   ├── main.py                   # Command-line single dataset processor
│   ├── batch_processor.py        # Batch processing for multiple files
│   └── one_command.py           # One-command batch processor
│
├── 📚 DOCUMENTATION
│   ├── docs/
│   │   ├── HOW_TO_RUN.md        # Quick start guide
│   │   ├── BATCH_PROCESSING_GUIDE.md # Multiple file processing
│   │   ├── LARGE_DATASET_GUIDE.md    # Handling large datasets
│   │   ├── STREAMLIT_GUIDE.md        # Web app guide
│   │   ├── DEPLOYMENT.md             # Deployment instructions
│   │   └── import_data_guide.md      # Data format guide
│   └── README.md                 # Main project documentation
│
├── 📊 DATA DIRECTORIES (Created automatically)
│   ├── data/                     # Input CSV files
│   └── results/                  # Analysis outputs
│
└── 🔒 DEPLOYMENT FILES
    ├── .gitignore               # Git ignore rules
    └── PROJECT_STRUCTURE.md     # This file
```

## 🎯 Key Files for Different Use Cases

### For Web App Users (Most Common)
- `streamlit_app.py` - Main application
- `src/` - Core analysis modules
- `requirements.txt` - Dependencies
- `docs/HOW_TO_RUN.md` - Getting started

### For Deployment
- `app.py` - Entry point
- `Procfile` - Deployment config
- `requirements.txt` - Dependencies
- `.streamlit/config.toml` - App settings

### For Command Line Users
- `scripts/main.py` - Single dataset processing
- `scripts/batch_processor.py` - Multiple datasets
- `scripts/one_command.py` - Simplified batch processing

### For Developers
- `src/` - Core modules for customization
- `config/` - Configuration files
- `docs/` - Comprehensive documentation

## 🚀 Quick Start

1. **Web Application**: `streamlit run streamlit_app.py`
2. **Command Line**: `python scripts/main.py`
3. **Batch Processing**: `python scripts/one_command.py data_folder/`

## 📦 Deployment Ready

This structure is optimized for:
- Streamlit Cloud
- Heroku
- AWS/GCP/Azure
- Local deployment