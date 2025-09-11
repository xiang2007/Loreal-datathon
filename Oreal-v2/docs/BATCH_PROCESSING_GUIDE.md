# 📊 Batch Processing Guide - Multiple Files, One Command

## 🎯 Overview
Process multiple CSV file pairs with a single command or through the web interface. Perfect for analyzing multiple datasets, time periods, or different video categories.

## 🚀 Quick Start Options

### Option 1: One Command Line (Simplest)
```bash
# Process all CSV files in current directory
python one_command.py

# Process files in specific directory
python one_command.py data/

# With custom output directory
python one_command.py --input data/ --output results/

# With sampling for large datasets
python one_command.py data/ --sample 50000
```

### Option 2: Batch Processor
```bash
# 1. Put CSV files in batch_input folder
# 2. Run batch processor
python batch_processor.py

# Or with custom directories
python batch_processor.py --input my_data/ --output my_results/
```

### Option 3: Windows Batch File
```bash
# 1. Put CSV files in batch_input folder
# 2. Double-click run_batch.bat
```

### Option 4: Web Interface (Streamlit)
```bash
# 1. Run streamlit app
streamlit run streamlit_app.py

# 2. Choose "Multiple Datasets (Batch)" mode
# 3. Upload multiple files at once
# 4. Click "Start Batch Processing"
```

## 📁 File Organization

### Automatic File Detection
The system automatically detects file types:

**Comment Files** (detected by):
- Filename contains 'comment' (e.g., `dataset1_comments.csv`)
- Has `textOriginal` column

**Video Files** (detected by):
- Filename contains 'video' (e.g., `dataset1_videos.csv`)
- Has `title` column

### Example Directory Structure
```
your_data/
├── jan_comments.csv          # January comments
├── jan_videos.csv           # January videos
├── feb_comments.csv         # February comments  
├── feb_videos.csv          # February videos
├── brand_a_comments.csv    # Brand A comments
├── brand_a_videos.csv     # Brand A videos
└── brand_b_comments.csv   # Brand B comments (no matching video file)
```

### File Matching Logic
1. **Exact match**: `dataset1_comments.csv` ↔ `dataset1_videos.csv`
2. **Partial match**: `jan_comments.csv` ↔ `jan_videos.csv`
3. **No match**: Comment file processed without video metadata

## 🔧 Processing Options

### Command Line Options
```bash
python one_command.py [directory] [options]

Options:
  --input, -i     Input directory path
  --output, -o    Output directory path (default: analysis_results)
  --sample, -s    Sample size for large datasets
  --quiet, -q     Suppress detailed output
```

### Web Interface Options
- **Combine Results**: Merge all datasets into single analysis
- **Individual Reports**: Generate separate reports per dataset
- **Sampling**: Automatically sample large datasets
- **Custom Sample Size**: Set sample size for each dataset

## 📊 Output Structure

### Generated Files
```
analysis_results/
├── batch_summary.txt           # Overall summary
├── dataset_01_analyzed.csv     # Full analysis results
├── dataset_01_report.txt       # Individual report
├── dataset_02_analyzed.csv     # Next dataset results
├── dataset_02_report.txt       # Next dataset report
└── combined_analysis.csv       # Combined results (if requested)
```

### Report Contents
Each report includes:
- **Overview metrics** (total comments, spam rate, quality scores)
- **Sentiment distribution** (positive/neutral/negative percentages)
- **Relevance breakdown** (genuine/general/spam categories)
- **Engagement analysis** (questions, suggestions, praise, etc.)
- **AI-generated insights** and recommendations
- **Top discussion topics** from genuine comments

## 🎯 Use Cases

### 1. Time Series Analysis
```
monthly_data/
├── 2024_01_comments.csv
├── 2024_01_videos.csv
├── 2024_02_comments.csv
├── 2024_02_videos.csv
└── ...
```
**Command**: `python one_command.py monthly_data/`

### 2. Brand Comparison
```
brand_analysis/
├── loreal_comments.csv
├── loreal_videos.csv
├── competitor_comments.csv
├── competitor_videos.csv
└── ...
```
**Command**: `python one_command.py brand_analysis/ --output brand_results/`

### 3. Product Category Analysis
```
products/
├── skincare_comments.csv
├── skincare_videos.csv
├── makeup_comments.csv
├── makeup_videos.csv
└── ...
```
**Command**: `python one_command.py products/ --sample 25000`

### 4. Regional Analysis
```
regions/
├── us_comments.csv
├── us_videos.csv
├── eu_comments.csv
├── eu_videos.csv
└── ...
```

## 📈 Performance Optimization

### For Large Datasets
- **Automatic sampling** for datasets > 100k comments
- **Batch processing** with optimized memory usage
- **Progress tracking** with ETA estimates
- **Resource monitoring** and warnings

### Recommended Limits
| Dataset Size | Processing Time | Memory Usage | Recommendation |
|-------------|----------------|--------------|----------------|
| < 10k comments | 1-2 min | 1-2 GB | Full processing |
| 10k-50k comments | 3-8 min | 2-4 GB | Full processing |
| 50k-100k comments | 8-15 min | 4-6 GB | Consider sampling |
| > 100k comments | 15+ min | 6+ GB | Use sampling |

### Sampling Strategy
```bash
# For very large datasets, use sampling
python one_command.py large_data/ --sample 50000

# This processes 50k representative comments from each dataset
# while maintaining statistical significance
```

## 🔍 Quality Assurance

### Automatic Validation
- **Column validation** for required fields
- **Data type checking** and conversion
- **Missing data handling** with appropriate defaults
- **Error reporting** with specific file and line information

### Error Handling
- **Individual file failures** don't stop batch processing
- **Detailed error logs** for troubleshooting
- **Partial results** saved even if some files fail
- **Recovery suggestions** for common issues

## 💡 Pro Tips

### 1. File Naming Best Practices
```
# Good naming (auto-detected)
dataset1_comments.csv / dataset1_videos.csv
jan2024_comments.csv / jan2024_videos.csv
skincare_comments.csv / skincare_videos.csv

# Avoid ambiguous names
data1.csv / data2.csv
file_a.csv / file_b.csv
```

### 2. Optimize Processing Speed
- **Use SSD storage** for faster I/O
- **Close other applications** to free memory
- **Process during off-peak hours** for system resources
- **Use sampling** for initial exploration

### 3. Organize Results
```bash
# Create dated output directories
python one_command.py data/ --output results_2024_03_15/

# Separate by analysis type
python one_command.py monthly/ --output monthly_analysis/
python one_command.py brands/ --output brand_comparison/
```

### 4. Combine with External Tools
```bash
# Export results for further analysis
# Results are CSV-compatible with Excel, R, Python pandas
```

## 🚨 Troubleshooting

### Common Issues

**"No CSV files found"**
- Check file extensions (.csv)
- Verify directory path
- Ensure files aren't in subdirectories

**"No comment files detected"**
- Ensure files have `textOriginal` column
- Check file encoding (should be UTF-8)
- Verify column names match exactly

**"Memory error during processing"**
- Use sampling: `--sample 25000`
- Process fewer files at once
- Close other applications
- Restart the system

**"Files not matching correctly"**
- Use consistent naming convention
- Check for typos in filenames
- Manually verify file contents

### Performance Issues
```bash
# If processing is slow:
python one_command.py data/ --sample 10000 --quiet

# If memory usage is high:
# Process files individually or use smaller samples
```

## 📞 Getting Help

### Debug Mode
```bash
# Run with detailed output
python one_command.py data/ --verbose

# Check individual file processing
python test_analysis.py
```

### Log Files
- Check `batch_summary.txt` for overview
- Individual reports contain detailed metrics
- Error messages include specific file and line information

## 🎉 Success Metrics

Your batch processing is successful when:
- ✅ All files are detected and categorized correctly
- ✅ Processing completes without memory errors
- ✅ Results are generated for each dataset
- ✅ Summary report shows expected metrics
- ✅ Individual reports contain meaningful insights
- ✅ Combined analysis (if requested) includes all datasets

**Ready to process multiple datasets with a single command!** 🚀