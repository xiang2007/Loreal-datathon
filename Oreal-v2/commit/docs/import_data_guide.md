# How to Import Your Own CSV Data

## Step 1: Prepare Your CSV Files

### Comments File Format (`data/comments.csv`)
```csv
videoId,textOriginal,likeCount,replyCount,publishedAt
ABC123,"Love this tutorial!",5,0,2024-01-15T10:30:00Z
ABC123,"What lipstick is that?",2,1,2024-01-15T11:00:00Z
DEF456,"Amazing transformation!",8,0,2024-01-16T09:20:00Z
```

**Required columns:**
- `videoId` - YouTube video identifier
- `textOriginal` - The actual comment text

**Optional columns:**
- `likeCount` - Number of likes on comment
- `replyCount` - Number of replies
- `publishedAt` - Timestamp when posted

### Videos File Format (`data/videos.csv`)
```csv
videoId,title,description,viewCount,likeCount,commentCount
ABC123,"Makeup Tutorial","Learn basic makeup",10000,500,25
DEF456,"Skincare Routine","Daily skincare tips",15000,750,40
```

**Required columns:**
- `videoId` - Must match videoId in comments file
- `title` - Video title

**Optional columns:**
- `description` - Video description (helps with relevance analysis)
- `viewCount`, `likeCount`, `commentCount` - Video metrics

## Step 2: Replace Sample Files

1. **Save your files as:**
   - `data/comments.csv`
   - `data/videos.csv`

2. **Make sure:**
   - Files are UTF-8 encoded
   - videoId values match between both files
   - No extra spaces in column names
   - Text with commas is properly quoted

## Step 3: Run Analysis

```bash
python main.py
```

## Step 4: View Results

Check the `results/` folder for:
- `analyzed_comments.csv` - Full analysis results
- `analysis_report.txt` - Summary report
- `*.png` - Visualization charts

## Troubleshooting

**File not found error?**
- Make sure files are named exactly `comments.csv` and `videos.csv`
- Check they're in the `data/` folder

**Encoding issues?**
- Save files as UTF-8 encoding
- Use quotes around text with special characters

**Missing columns?**
- Only `videoId` and `textOriginal` are required for comments
- Only `videoId` and `title` are required for videos
- Other columns are optional but recommended

**Empty results?**
- Check that videoId values match between files
- Ensure comment text isn't empty
- Verify CSV format is correct