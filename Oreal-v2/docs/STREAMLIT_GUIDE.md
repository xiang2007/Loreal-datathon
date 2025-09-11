# 🌐 Streamlit Web App Guide

## 🚀 Getting Started

### 1. Launch the Application
**Windows Users:**
- Double-click `run_app.bat`

**Mac/Linux Users:**
```bash
python run_streamlit.py
```

### 2. Access the Web Interface
- The app will automatically open in your browser
- If not, go to: `http://localhost:8501`

## 📤 Uploading Your Data

### Step 1: Prepare Your CSV Files
You need **two CSV files**:

#### Comments File (Required columns)
- `videoId` - Video identifier
- `textOriginal` - The comment text
- `likeCount` - Number of likes (optional)
- `replyCount` - Number of replies (optional)
- `publishedAt` - When posted (optional)

#### Videos File (Required columns)
- `videoId` - Video identifier (must match comments)
- `title` - Video title
- `description` - Video description (optional)
- `viewCount` - View count (optional)
- `likeCount` - Video likes (optional)
- `commentCount` - Total comments (optional)

### Step 2: Upload Files
1. Go to the "📤 Upload Data" page
2. Drag & drop or click to upload your CSV files
3. The app will validate your data automatically
4. Click "🚀 Start Analysis" when both files are uploaded

## 🔍 Exploring Results

### Analysis Results Page
- View overview metrics (total comments, spam rate, quality scores)
- See detailed breakdowns with interactive charts
- Filter results by relevance, sentiment, and quality
- Browse sample comments with their classifications

### Visualizations Page
- Interactive charts showing engagement patterns
- Quality vs engagement correlations
- Sentiment trends over time (if dates available)
- Video-level performance analysis

### Insights Page
- AI-generated insights and recommendations
- Top discussion topics from genuine comments
- Engagement recommendations based on patterns
- Custom analysis suggestions

### Export Page
- Download full results as CSV
- Generate summary reports
- Preview data with custom column selection
- Quick statistics overview

## 🎯 Key Features

### Real-time Processing
- Progress bars show analysis status
- Batch processing for large datasets
- Error handling with helpful messages

### Interactive Filtering
- Filter by relevance (genuine/general/spam)
- Filter by sentiment (positive/neutral/negative)
- Minimum quality score slider
- Real-time result updates

### Smart Validation
- Automatic column detection
- Missing data handling
- Format validation with helpful error messages
- Preview data before analysis

### Export Options
- CSV download with timestamp
- Text summary reports
- Customizable column selection
- Formatted insights and recommendations

## 🔧 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**CSV upload fails:**
- Check file encoding (should be UTF-8)
- Ensure required columns are present
- Remove any special characters from column names

**Analysis takes too long:**
- The app processes in batches for large datasets
- Progress bars show current status
- Consider using a sample of your data for initial testing

**Charts not displaying:**
- Refresh the page
- Check browser console for JavaScript errors
- Try a different browser (Chrome/Firefox recommended)

### Performance Tips

**For Large Datasets (>10k comments):**
- Upload a sample first to test
- Use filtering to focus on specific segments
- Export results for further analysis in Excel/Python

**For Better Results:**
- Include video titles and descriptions for better relevance classification
- Ensure comment text is clean (remove excessive formatting)
- Include like counts for better quality scoring

## 📊 Understanding the Analysis

### Quality Score (0-5)
- **0-1**: Low quality (spam, very short, irrelevant)
- **2-3**: Medium quality (general engagement, basic comments)
- **4-5**: High quality (questions, detailed feedback, genuine engagement)

### Relevance Categories
- **Genuine**: On-topic, relates to video content
- **General**: Generic but not spam (e.g., "nice video")
- **Spam**: Self-promotion, irrelevant, bot-like

### Engagement Types
- **Question**: Asks for information or clarification
- **Suggestion**: Provides recommendations or ideas
- **Technique Request**: Asks for tutorials or how-to content
- **Praise**: Positive feedback and compliments
- **Thanks**: Expressions of gratitude
- **General**: Other types of engagement

### Sentiment Analysis
- **Positive**: Happy, satisfied, enthusiastic comments
- **Neutral**: Factual, questions, neutral observations
- **Negative**: Criticism, complaints, dissatisfaction (not necessarily bad if constructive)

## 🎉 Next Steps

After analyzing your data:

1. **Review Key Insights** - Check the AI-generated recommendations
2. **Export Results** - Download CSV for further analysis
3. **Share Findings** - Use the summary report for presentations
4. **Iterate** - Upload new data to track changes over time
5. **Take Action** - Implement recommendations to improve engagement

## 💡 Pro Tips

- **Regular Analysis**: Upload new data monthly to track trends
- **Segment Analysis**: Filter by video type or time period for deeper insights
- **Quality Focus**: Use quality scores to identify your best-performing content
- **Topic Mining**: Review extracted topics to understand audience interests
- **Engagement Strategy**: Use engagement type data to plan content calendar