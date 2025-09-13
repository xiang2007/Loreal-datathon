# 💄 L'Oréal YouTube Comment Quality Analysis

AI-powered analysis of YouTube comment quality to understand engagement patterns and content performance.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web application
streamlit run streamlit_app.py
```

Open `http://localhost:8501` in your browser and upload your CSV files!

## ✨ Features

- **📤 Drag & Drop Upload**: Easy CSV file upload with validation
- **🤖 AI Analysis**: Automated comment classification and sentiment analysis
- **📊 Interactive Dashboard**: Real-time visualizations and insights
- **📈 Batch Processing**: Handle multiple datasets simultaneously
- **💡 Smart Insights**: AI-generated recommendations and trends
- **📋 Export Results**: Download analysis in multiple formats

## 📁 Data Requirements

Upload two CSV files:

### 1. Comments File
```csv
videoId,textOriginal,likeCount,replyCount,publishedAt
vid123,"Love this tutorial!",15,2,2024-01-15T10:30:00Z
```
**Required:** `videoId`, `textOriginal` | **Optional:** `likeCount`, `replyCount`, `publishedAt`

### 2. Videos File  
```csv
videoId,title,description,viewCount,likeCount,commentCount
vid123,"Makeup Tutorial","Daily routine",50000,1200,89
```
**Required:** `videoId`, `title` | **Optional:** `description`, `viewCount`, `likeCount`, `commentCount`

## 🎯 What You Get

- **Comment Classification**: Genuine vs General vs Spam
- **Sentiment Analysis**: Positive, Neutral, Negative with confidence scores
- **Engagement Types**: Questions, Suggestions, Praise, Technique Requests
- **Quality Scoring**: 0-5 scale based on relevance, sentiment, and engagement
- **Topic Extraction**: Key themes from genuine comments
- **Performance Insights**: Actionable recommendations for content strategy

## 📊 Sample Analysis

Try the app with the included sample files in the `data/` folder:
- `sample_comments.csv` - Example comment data
- `sample_videos.csv` - Example video metadata

## 🔧 Advanced Usage

### Command Line Processing
```bash
# Single dataset
python scripts/main.py

# Batch processing
python scripts/one_command.py your_data_folder/
```

### Large Datasets (50k+ comments)
The app automatically optimizes for large datasets with:
- Smart sampling options
- Batch processing
- Memory management
- Progress tracking

## 📋 Project Structure

```
├── 📱 streamlit_app.py     # Main web application
├── 📱 app.py              # Deployment entry point
├── 🧠 src/                # Core analysis modules
├── ⚙️ config/             # Configuration files
├── 🔧 scripts/            # Command-line tools
├── 📚 docs/               # Documentation
├── 📊 data/               # Sample data files
└── 📋 requirements.txt    # Dependencies
```

## 🌐 Deployment Ready

Deploy instantly on:
- **Streamlit Cloud** (recommended)
- **Heroku**
- **AWS/GCP/Azure**
- **Local servers**

## 📖 Documentation

- [How to Run](docs/HOW_TO_RUN.md) - Detailed setup guide
- [Batch Processing](docs/BATCH_PROCESSING_GUIDE.md) - Multiple file handling
- [Large Datasets](docs/LARGE_DATASET_GUIDE.md) - Performance optimization
- [Deployment](docs/DEPLOYMENT.md) - Cloud deployment guide

## 🎉 Ready to Analyze!

1. **Upload** your YouTube comment and video CSV files
2. **Analyze** with AI-powered classification and sentiment analysis  
3. **Explore** interactive visualizations and insights
4. **Export** results for presentations and further analysis
5. **Optimize** your content strategy based on recommendations

Perfect for social media managers, content creators, and marketing teams! 🚀