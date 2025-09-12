"""
Streamlit Web Application for L'Oréal YouTube Comment Quality Analysis
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import sys
import tempfile
import zipfile
import gc
import psutil
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src directory to path
sys.path.append('src')

# Import large dataset configurations
try:
    from config.large_dataset_config import *
except ImportError:
    # Fallback configuration if file not found
    LARGE_DATASET_CONFIG = {
        'batch_sizes': {'small': 250, 'medium': 500, 'large': 1000, 'xlarge': 2000},
        'sampling': {'enable_sampling_above': 100000}
    }

try:
    from src.data_processing import DataProcessor
    from src.analysis import CommentAnalyzer
    from src.dashboard import CommentDashboard
    from src.ai_assistant import AIAssistant
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="L'Oréal Comment Analysis",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #E31837;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #E31837;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">💄 L\'Oréal YouTube Comment Quality Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🤖 AI-Powered Analysis Dashboard")
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Navigation
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📤 Upload Data", "🔍 Analysis Results", "📈 Visualizations", "🤖 AI Insights & Assistant", "📋 Data Export"]
    )
    
    # AI Quick Summary in Sidebar
    if st.session_state.analysis_complete and st.session_state.analysis_results is not None:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 AI Quick Summary")
        
        df = st.session_state.analysis_results
        ai_assistant = AIAssistant(df)
        
        # Quick metrics
        total_comments = len(df)
        spam_rate = (df.get('is_spam', pd.Series()) == True).mean() * 100
        avg_quality = df.get('quality_score', pd.Series()).mean()
        
        st.sidebar.metric("Total Comments", f"{total_comments:,}")
        st.sidebar.metric("Spam Rate", f"{spam_rate:.1f}%", 
                         delta="Good" if spam_rate < 10 else "High")
        st.sidebar.metric("Quality Score", f"{avg_quality:.2f}/5",
                         delta="Excellent" if avg_quality > 3.5 else "Good" if avg_quality > 2.5 else "Needs Work")
        
        # Quick AI insight
        if st.sidebar.button("💡 Get Quick AI Insight"):
            insight = ai_assistant._get_key_insight()
            st.sidebar.info(f"💡 {insight}")
    
    # Main page routing
    if page == "📤 Upload Data":
        upload_page()
    elif page == "🔍 Analysis Results":
        analysis_page()
    elif page == "📈 Visualizations":
        visualization_page()
    elif page == "🤖 AI Insights & Assistant":
        insights_page()
    elif page == "📋 Data Export":
        export_page()

def check_system_resources():
    """Check system resources for large dataset processing"""
    try:
        memory = psutil.virtual_memory()
        return {
            'total_memory_gb': memory.total / (1024**3),
            'available_memory_gb': memory.available / (1024**3),
            'memory_percent': memory.percent,
            'cpu_count': psutil.cpu_count()
        }
    except:
        return None

def upload_page():
    st.header("📤 Upload Your Data")
    
    # Upload mode selection
    upload_mode = st.radio(
        "Choose upload mode:",
        ["Single Dataset", "Multiple Datasets (Batch)"],
        horizontal=True
    )
    
    # System resources info
    resources = check_system_resources()
    if resources:
        with st.expander("💻 System Resources", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Available Memory", f"{resources['available_memory_gb']:.1f} GB")
            with col2:
                st.metric("CPU Cores", resources['cpu_count'])
            with col3:
                memory_status = "Good" if resources['memory_percent'] < 70 else "Limited" if resources['memory_percent'] < 85 else "Low"
                st.metric("Memory Usage", f"{resources['memory_percent']:.0f}%", delta=memory_status)
            
            if resources['available_memory_gb'] < 2:
                st.error("⚠️ Low memory detected. Large datasets may fail to process.")
            elif resources['available_memory_gb'] < 4:
                st.warning("⚠️ Limited memory. Consider using sampling for datasets > 50k comments.")
    
    if upload_mode == "Single Dataset":
        upload_single_dataset()
    else:
        upload_multiple_datasets()

def upload_single_dataset():
    """Handle single dataset upload"""
    # Instructions
    with st.expander("📋 Data Format Requirements", expanded=True):
        st.markdown("""
        **Required CSV Files:**
        
        **1. Comments File** - Must contain:
        - `videoId`: Video identifier
        - `textOriginal`: Comment text
        - `likeCount`: Number of likes (optional)
        - `replyCount`: Number of replies (optional)
        - `publishedAt`: Timestamp (optional)
        
        **2. Videos File** - Must contain:
        - `videoId`: Video identifier (must match comments)
        - `title`: Video title
        - `description`: Video description (optional)
        - `viewCount`: View count (optional)
        - `likeCount`: Video likes (optional)
        - `commentCount`: Total comments (optional)
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Comments Data")
        comments_file = st.file_uploader(
            "Upload comments CSV file",
            type=['csv'],
            key="comments_upload",
            help="CSV file containing YouTube comments data"
        )
        
        if comments_file is not None:
            try:
                comments_df = pd.read_csv(comments_file)
                st.success(f"✅ Loaded {len(comments_df)} comments")
                
                # Show preview
                st.write("**Preview:**")
                st.dataframe(comments_df.head(), use_container_width=True)
                
                # Validate required columns
                required_cols = ['videoId', 'textOriginal']
                missing_cols = [col for col in required_cols if col not in comments_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {missing_cols}")
                else:
                    st.success("✅ All required columns present")
                    
                    # Show optional columns status
                    optional_cols = ['likeCount', 'replyCount', 'publishedAt']
                    available_optional = [col for col in optional_cols if col in comments_df.columns]
                    missing_optional = [col for col in optional_cols if col not in comments_df.columns]
                    
                    if available_optional:
                        st.info(f"📊 Optional columns found: {', '.join(available_optional)}")
                    if missing_optional:
                        st.info(f"ℹ️ Optional columns missing: {', '.join(missing_optional)} (analysis will continue without these)")
                    
            except Exception as e:
                st.error(f"❌ Error reading comments file: {e}")
    
    with col2:
        st.subheader("🎥 Videos Data")
        videos_file = st.file_uploader(
            "Upload videos CSV file",
            type=['csv'],
            key="videos_upload",
            help="CSV file containing YouTube videos metadata"
        )
        
        if videos_file is not None:
            try:
                videos_df = pd.read_csv(videos_file)
                st.success(f"✅ Loaded {len(videos_df)} videos")
                
                # Show preview
                st.write("**Preview:**")
                st.dataframe(videos_df.head(), use_container_width=True)
                
                # Validate required columns
                required_cols = ['videoId', 'title']
                missing_cols = [col for col in required_cols if col not in videos_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {missing_cols}")
                else:
                    st.success("✅ All required columns present")
                    
            except Exception as e:
                st.error(f"❌ Error reading videos file: {e}")
    
    # Analysis button
    if comments_file is not None and videos_file is not None:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
                run_analysis(comments_df, videos_df)

def upload_multiple_datasets():
    """Handle multiple dataset upload and batch processing"""
    st.subheader("📊 Batch Processing Mode")
    
    with st.expander("📋 Batch Processing Instructions", expanded=True):
        st.markdown("""
        **Upload Multiple Files:**
        1. Upload multiple comment and video CSV files
        2. Files will be automatically matched by name similarity
        3. All datasets will be processed in sequence
        4. Results will be combined into a comprehensive report
        
        **File Naming Convention:**
        - Comment files: Include 'comment' in filename (e.g., `dataset1_comments.csv`)
        - Video files: Include 'video' in filename (e.g., `dataset1_videos.csv`)
        - Or ensure comment files have `textOriginal` column for auto-detection
        """)
    
    # Multiple file upload
    st.subheader("📁 Upload Multiple Files")
    
    uploaded_files = st.file_uploader(
        "Upload multiple CSV files (comments and videos)",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload all your CSV files at once. The system will automatically detect and match comment/video pairs."
    )
    
    if uploaded_files:
        st.success(f"✅ Uploaded {len(uploaded_files)} files")
        
        # Categorize files
        comment_files = []
        video_files = []
        unknown_files = []
        
        for file in uploaded_files:
            filename = file.name.lower()
            
            # Try to categorize by filename
            if 'comment' in filename:
                comment_files.append(file)
            elif 'video' in filename:
                video_files.append(file)
            else:
                # Try to detect by content
                try:
                    df_sample = pd.read_csv(file, nrows=1)
                    if 'textOriginal' in df_sample.columns:
                        comment_files.append(file)
                    elif 'title' in df_sample.columns:
                        video_files.append(file)
                    else:
                        unknown_files.append(file)
                    file.seek(0)  # Reset file pointer
                except:
                    unknown_files.append(file)
        
        # Show categorization results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Comment Files", len(comment_files))
            if comment_files:
                with st.expander("Comment Files"):
                    for f in comment_files:
                        st.write(f"📝 {f.name}")
        
        with col2:
            st.metric("Video Files", len(video_files))
            if video_files:
                with st.expander("Video Files"):
                    for f in video_files:
                        st.write(f"🎥 {f.name}")
        
        with col3:
            st.metric("Unknown Files", len(unknown_files))
            if unknown_files:
                with st.expander("Unknown Files"):
                    for f in unknown_files:
                        st.write(f"❓ {f.name}")
                st.warning("Unknown files will be skipped. Please check file format.")
        
        # Batch processing options
        if comment_files:
            st.markdown("---")
            st.subheader("⚙️ Batch Processing Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                combine_results = st.checkbox("Combine all results into single report", value=True)
                generate_individual_reports = st.checkbox("Generate individual reports per dataset", value=True)
            
            with col2:
                use_sampling = st.checkbox("Use sampling for large datasets (>50k comments)", value=True)
                if use_sampling:
                    sample_size = st.slider("Sample size per dataset", 10000, 100000, 50000, 10000)
            
            # Start batch processing
            if st.button("🚀 Start Batch Processing", type="primary", use_container_width=True):
                run_batch_analysis(
                    comment_files, 
                    video_files, 
                    combine_results, 
                    generate_individual_reports,
                    use_sampling,
                    sample_size if use_sampling else None
                )
        else:
            st.error("❌ No comment files detected. Please upload files with 'textOriginal' column.")

def run_analysis(comments_df, videos_df):
    """Run the complete analysis pipeline optimized for large datasets"""
    
    # Check dataset size and warn user
    total_comments = len(comments_df)
    if total_comments > 50000:
        st.warning(f"⚠️ Large dataset detected ({total_comments:,} comments). This may take several minutes to process.")
        
        # Offer sampling option for very large datasets
        if total_comments > 100000:
            col1, col2 = st.columns(2)
            with col1:
                use_sample = st.checkbox("Use sample for faster processing", value=True)
            with col2:
                if use_sample:
                    sample_size = st.slider("Sample size", 10000, 100000, 50000, 10000)
                    comments_df = comments_df.sample(n=sample_size, random_state=42)
                    st.info(f"Using sample of {len(comments_df):,} comments")
    
    with st.spinner("🔄 Processing data..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Data Processing
            status_text.text("📊 Processing and merging data...")
            progress_bar.progress(10)
            
            processor = DataProcessor()
            processor.comments_df = comments_df
            processor.videos_df = videos_df
            
            if not processor.merge_datasets():
                st.error("❌ Failed to merge datasets")
                return
            
            progress_bar.progress(20)
            
            if not processor.preprocess_data():
                st.error("❌ Failed to preprocess data")
                return
            
            progress_bar.progress(30)
            
            # Step 2: Comment Analysis
            status_text.text("🔍 Analyzing comments...")
            analyzer = CommentAnalyzer()
            
            # Optimize batch size based on dataset size
            if len(processor.merged_df) > 50000:
                batch_size = 1000  # Larger batches for big datasets
            elif len(processor.merged_df) > 10000:
                batch_size = 500
            else:
                batch_size = 250
            
            all_results = []
            total_batches = (len(processor.merged_df) - 1) // batch_size + 1
            
            status_text.text(f"🔍 Analyzing {len(processor.merged_df):,} comments in {total_batches} batches...")
            
            for i in range(0, len(processor.merged_df), batch_size):
                batch_num = (i // batch_size) + 1
                batch = processor.merged_df.iloc[i:i+batch_size]
                
                status_text.text(f"🔍 Processing batch {batch_num}/{total_batches} ({len(batch)} comments)...")
                
                batch_results = analyzer.analyze_comment_batch(batch)
                all_results.append(batch_results)
                
                # Update progress (30% to 85%)
                progress = 30 + (55 * batch_num / total_batches)
                progress_bar.progress(min(int(progress), 85))
            
            # Combine results
            status_text.text("🔗 Combining analysis results...")
            progress_bar.progress(85)
            
            analysis_df = pd.concat(all_results, ignore_index=True)
            
            # Add quality scores efficiently
            status_text.text("⭐ Calculating quality scores...")
            progress_bar.progress(90)
            
            quality_scores = []
            for _, row in analysis_df.iterrows():
                if row['comment_id'] < len(processor.merged_df):
                    original_row = processor.merged_df.iloc[row['comment_id']]
                    # Handle missing likeCount column
                    like_count = 0
                    if 'likeCount' in processor.merged_df.columns:
                        like_count = original_row.get('likeCount', 0)
                        # Convert to numeric if it's a string
                        try:
                            like_count = float(like_count) if like_count else 0
                        except (ValueError, TypeError):
                            like_count = 0
                    
                    quality_score = analyzer.generate_quality_score(
                        row['relevance'], 
                        row['vader_sentiment'], 
                        row['engagement_type'],
                        like_count
                    )
                    quality_scores.append(quality_score)
                else:
                    quality_scores.append(0)
            
            analysis_df['quality_score'] = quality_scores
            
            # Merge with original data
            final_df = processor.merged_df.merge(
                analysis_df, 
                left_index=True, 
                right_on='comment_id', 
                how='left'
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store results in session state
            st.session_state.processed_data = processor.merged_df
            st.session_state.analysis_results = final_df
            st.session_state.analysis_complete = True
            
            # Show success message with performance info
            processing_time = "Processing completed"
            st.success(f"🎉 Analysis completed successfully! {processing_time}")
            
            # Show comprehensive stats
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Comments", f"{len(final_df):,}")
            
            with col2:
                spam_rate = (final_df['is_spam'] == True).mean() * 100
                st.metric("Spam Rate", f"{spam_rate:.1f}%")
            
            with col3:
                avg_quality = final_df['quality_score'].mean()
                st.metric("Avg Quality", f"{avg_quality:.2f}/5")
            
            with col4:
                unique_videos = final_df['videoId'].nunique()
                st.metric("Unique Videos", f"{unique_videos:,}")
            
            with col5:
                genuine_rate = (final_df['relevance'] == 'genuine').mean() * 100
                st.metric("Genuine Rate", f"{genuine_rate:.1f}%")
            
            # Performance summary for large datasets
            if len(final_df) > 10000:
                st.info(f"📊 Large dataset processed: {len(final_df):,} comments analyzed successfully!")
            
            st.info("👈 Navigate to other pages using the sidebar to explore results!")
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.exception(e)
            
            # Provide helpful error messages for large datasets
            if "memory" in str(e).lower():
                st.error("💾 Memory error detected. Try using a smaller sample size or restart the app.")
            elif "timeout" in str(e).lower():
                st.error("⏱️ Processing timeout. Large datasets may take longer - please be patient.")

def run_batch_analysis(comment_files, video_files, combine_results, generate_individual_reports, use_sampling, sample_size):
    """Run batch analysis on multiple file pairs"""
    
    st.header("🔄 Batch Processing in Progress")
    
    # Auto-match files
    file_pairs = auto_match_files(comment_files, video_files)
    
    if not file_pairs:
        st.error("❌ No valid file pairs found for processing")
        return
    
    st.info(f"📊 Processing {len(file_pairs)} dataset pairs...")
    
    # Initialize results storage
    all_results = []
    individual_results = []
    
    # Progress tracking
    overall_progress = st.progress(0)
    status_container = st.container()
    
    for i, (comment_file, video_file, pair_name) in enumerate(file_pairs):
        with status_container:
            st.subheader(f"📊 Processing Dataset {i+1}/{len(file_pairs)}: {pair_name}")
            
            try:
                # Load data
                comments_df = pd.read_csv(comment_file)
                
                if video_file:
                    videos_df = pd.read_csv(video_file)
                else:
                    # Create dummy videos dataframe
                    unique_videos = comments_df['videoId'].unique()
                    videos_df = pd.DataFrame({
                        'videoId': unique_videos,
                        'title': [f'Video {j}' for j in range(len(unique_videos))],
                        'description': [''] * len(unique_videos)
                    })
                
                # Apply sampling if requested
                if use_sampling and len(comments_df) > sample_size:
                    st.info(f"📊 Sampling {sample_size:,} comments from {len(comments_df):,} total")
                    comments_df = comments_df.sample(n=sample_size, random_state=42)
                
                # Process this dataset
                processor = DataProcessor()
                processor.comments_df = comments_df
                processor.videos_df = videos_df
                
                if processor.merge_datasets() and processor.preprocess_data():
                    analyzer = CommentAnalyzer()
                    
                    # Analyze in batches
                    batch_size = 1000 if len(processor.merged_df) > 10000 else 500
                    batch_results = []
                    
                    for j in range(0, len(processor.merged_df), batch_size):
                        batch = processor.merged_df.iloc[j:j+batch_size]
                        result = analyzer.analyze_comment_batch(batch)
                        batch_results.append(result)
                    
                    # Combine batch results
                    analysis_df = pd.concat(batch_results, ignore_index=True)
                    
                    # Add quality scores
                    quality_scores = []
                    for _, row in analysis_df.iterrows():
                        if row['comment_id'] < len(processor.merged_df):
                            original_row = processor.merged_df.iloc[row['comment_id']]
                            like_count = 0
                            if 'likeCount' in processor.merged_df.columns:
                                like_count = original_row.get('likeCount', 0)
                                try:
                                    like_count = float(like_count) if like_count else 0
                                except (ValueError, TypeError):
                                    like_count = 0
                            
                            quality_score = analyzer.generate_quality_score(
                                row['relevance'], 
                                row['vader_sentiment'], 
                                row['engagement_type'],
                                like_count
                            )
                            quality_scores.append(quality_score)
                        else:
                            quality_scores.append(0)
                    
                    analysis_df['quality_score'] = quality_scores
                    
                    # Merge with original data
                    final_df = processor.merged_df.merge(
                        analysis_df, 
                        left_index=True, 
                        right_on='comment_id', 
                        how='left'
                    )
                    
                    # Add dataset identifier
                    final_df['dataset_name'] = pair_name
                    
                    # Store results
                    if combine_results:
                        all_results.append(final_df)
                    
                    if generate_individual_reports:
                        individual_results.append({
                            'name': pair_name,
                            'data': final_df,
                            'total_comments': len(final_df),
                            'spam_rate': (final_df['is_spam'] == True).mean() * 100,
                            'avg_quality': final_df['quality_score'].mean(),
                            'positive_sentiment': (final_df['vader_sentiment'] == 'positive').mean() * 100
                        })
                    
                    st.success(f"✅ {pair_name} processed successfully! ({len(final_df):,} comments)")
                    
                else:
                    st.error(f"❌ Failed to process {pair_name}")
                    
            except Exception as e:
                st.error(f"❌ Error processing {pair_name}: {e}")
            
            # Update progress
            overall_progress.progress((i + 1) / len(file_pairs))
    
    # Process combined results
    if combine_results and all_results:
        st.header("📊 Combined Results")
        
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Store in session state
        st.session_state.processed_data = combined_df
        st.session_state.analysis_results = combined_df
        st.session_state.analysis_complete = True
        
        # Show combined metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Comments", f"{len(combined_df):,}")
        
        with col2:
            spam_rate = (combined_df['is_spam'] == True).mean() * 100
            st.metric("Overall Spam Rate", f"{spam_rate:.1f}%")
        
        with col3:
            avg_quality = combined_df['quality_score'].mean()
            st.metric("Avg Quality Score", f"{avg_quality:.2f}/5")
        
        with col4:
            positive_rate = (combined_df['vader_sentiment'] == 'positive').mean() * 100
            st.metric("Positive Sentiment", f"{positive_rate:.1f}%")
        
        with col5:
            datasets_count = combined_df['dataset_name'].nunique()
            st.metric("Datasets Processed", f"{datasets_count}")
        
        st.success("🎉 Batch processing completed! Navigate to other pages to explore results.")
    
    # Show individual results summary
    if generate_individual_reports and individual_results:
        st.header("📋 Individual Dataset Summary")
        
        summary_data = []
        for result in individual_results:
            summary_data.append({
                'Dataset': result['name'],
                'Comments': f"{result['total_comments']:,}",
                'Spam Rate': f"{result['spam_rate']:.1f}%",
                'Avg Quality': f"{result['avg_quality']:.2f}/5",
                'Positive %': f"{result['positive_sentiment']:.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

def auto_match_files(comment_files, video_files):
    """Automatically match comment and video files"""
    pairs = []
    used_video_files = set()
    
    for i, comment_file in enumerate(comment_files):
        comment_name = comment_file.name.lower()
        best_match = None
        best_score = 0
        
        # Try to find matching video file
        for video_file in video_files:
            if video_file.name in used_video_files:
                continue
                
            video_name = video_file.name.lower()
            
            # Calculate similarity score
            comment_base = comment_name.replace('comment', '').replace('.csv', '')
            video_base = video_name.replace('video', '').replace('.csv', '')
            
            # Simple similarity scoring
            score = 0
            if comment_base == video_base:
                score = 100
            elif comment_base in video_base or video_base in comment_base:
                score = 80
            elif any(part in video_base for part in comment_base.split('_') if len(part) > 2):
                score = 60
            
            if score > best_score:
                best_score = score
                best_match = video_file
        
        if best_match:
            used_video_files.add(best_match.name)
            pair_name = f"dataset_{i+1:02d}"
            pairs.append((comment_file, best_match, pair_name))
        else:
            # Use without video file
            pair_name = f"dataset_{i+1:02d}"
            pairs.append((comment_file, None, pair_name))
    
    return pairs

def analysis_page():
    st.header("🔍 Analysis Results")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    # Overview metrics
    st.subheader("📊 Overview Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_comments = len(df)
        st.metric("Total Comments", f"{total_comments:,}")
    
    with col2:
        spam_rate = (df['is_spam'] == True).mean() * 100
        st.metric("Spam Rate", f"{spam_rate:.1f}%", delta=f"{spam_rate-15:.1f}%" if spam_rate < 15 else None)
    
    with col3:
        avg_quality = df['quality_score'].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.2f}/5")
    
    with col4:
        positive_rate = (df['vader_sentiment'] == 'positive').mean() * 100
        st.metric("Positive Sentiment", f"{positive_rate:.1f}%")
    
    with col5:
        unique_videos = df['videoId'].nunique()
        st.metric("Unique Videos", f"{unique_videos:,}")
    
    # Detailed breakdown
    st.subheader("📈 Detailed Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Relevance Distribution**")
        relevance_counts = df['relevance'].value_counts()
        fig_relevance = px.pie(
            values=relevance_counts.values,
            names=relevance_counts.index,
            title="Comment Relevance",
            color_discrete_map={
                'genuine': '#2E8B57',
                'general': '#4682B4',
                'spam': '#DC143C'
            }
        )
        st.plotly_chart(fig_relevance, use_container_width=True)
    
    with col2:
        st.write("**Sentiment Distribution**")
        sentiment_counts = df['vader_sentiment'].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Comment Sentiment",
            color_discrete_map={
                'positive': '#32CD32',
                'neutral': '#FFD700',
                'negative': '#FF6347'
            }
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # Data table
    st.subheader("📋 Sample Results")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        relevance_filter = st.selectbox(
            "Filter by Relevance:",
            ["All"] + list(df['relevance'].unique())
        )
    
    with col2:
        sentiment_filter = st.selectbox(
            "Filter by Sentiment:",
            ["All"] + list(df['vader_sentiment'].unique())
        )
    
    with col3:
        min_quality = st.slider(
            "Minimum Quality Score:",
            0.0, 5.0, 0.0, 0.1
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if relevance_filter != "All":
        filtered_df = filtered_df[filtered_df['relevance'] == relevance_filter]
    
    if sentiment_filter != "All":
        filtered_df = filtered_df[filtered_df['vader_sentiment'] == sentiment_filter]
    
    filtered_df = filtered_df[filtered_df['quality_score'] >= min_quality]
    
    # Display filtered results
    display_columns = [
        'textOriginal_cleaned', 'relevance', 'vader_sentiment', 
        'engagement_type', 'quality_score', 'likeCount'
    ]
    
    available_columns = [col for col in display_columns if col in filtered_df.columns]
    
    if available_columns:
        st.dataframe(
            filtered_df[available_columns].head(100),
            use_container_width=True
        )
    else:
        st.warning("No data columns available for display. Please check your data format.")
    
    st.info(f"Showing {len(filtered_df)} comments (filtered from {len(df)} total)")

def visualization_page():
    st.header("📈 Visualizations")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    # Engagement Types
    st.subheader("🎯 Engagement Types")
    engagement_counts = df['engagement_type'].value_counts()
    
    fig_engagement = px.bar(
        x=engagement_counts.index,
        y=engagement_counts.values,
        title="Distribution of Engagement Types",
        labels={'x': 'Engagement Type', 'y': 'Number of Comments'},
        color=engagement_counts.values,
        color_continuous_scale='viridis'
    )
    fig_engagement.update_layout(showlegend=False)
    st.plotly_chart(fig_engagement, use_container_width=True)
    
    # Quality vs Likes correlation
    st.subheader("⭐ Quality vs Engagement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality score distribution
        fig_quality = px.histogram(
            df, 
            x='quality_score',
            title="Quality Score Distribution",
            nbins=20,
            labels={'quality_score': 'Quality Score', 'count': 'Number of Comments'}
        )
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Quality vs Likes scatter
        if 'likeCount' in df.columns and 'quality_score' in df.columns:
            # Filter outliers for better visualization
            df_filtered = df[df['likeCount'] <= df['likeCount'].quantile(0.95)]
            
            fig_scatter = px.scatter(
                df_filtered,
                x='quality_score',
                y='likeCount',
                color='vader_sentiment',
                title="Quality Score vs Like Count",
                labels={'quality_score': 'Quality Score', 'likeCount': 'Like Count'},
                color_discrete_map={
                    'positive': '#32CD32',
                    'neutral': '#FFD700',
                    'negative': '#FF6347'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            # Alternative visualization if likeCount is not available
            if 'quality_score' in df.columns:
                fig_alt = px.box(
                    df,
                    x='vader_sentiment',
                    y='quality_score',
                    title="Quality Score by Sentiment",
                    labels={'quality_score': 'Quality Score', 'vader_sentiment': 'Sentiment'},
                    color='vader_sentiment',
                    color_discrete_map={
                        'positive': '#32CD32',
                        'neutral': '#FFD700',
                        'negative': '#FF6347'
                    }
                )
                st.plotly_chart(fig_alt, use_container_width=True)
            else:
                st.info("Quality scores not available for visualization")
    
    # Sentiment over time (if timestamp available)
    if 'publishedAt' in df.columns:
        st.subheader("📅 Sentiment Trends Over Time")
        
        try:
            df['date'] = pd.to_datetime(df['publishedAt']).dt.date
            sentiment_time = df.groupby(['date', 'vader_sentiment']).size().reset_index(name='count')
            
            fig_time = px.line(
                sentiment_time,
                x='date',
                y='count',
                color='vader_sentiment',
                title="Sentiment Trends Over Time",
                labels={'date': 'Date', 'count': 'Number of Comments'},
                color_discrete_map={
                    'positive': '#32CD32',
                    'neutral': '#FFD700',
                    'negative': '#FF6347'
                }
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
        except Exception as e:
            st.warning(f"Could not create time series: {e}")
    
    # Video-level analysis
    st.subheader("🎥 Video-Level Analysis")
    
    if 'title' in df.columns:
        # Build aggregation dictionary based on available columns
        agg_dict = {
            'quality_score': 'mean',
            'textOriginal_cleaned': 'count'
        }
        
        # Add likeCount aggregation only if column exists
        if 'likeCount' in df.columns:
            agg_dict['likeCount'] = 'sum'
            column_names = ['Avg Quality', 'Comment Count', 'Total Likes']
        else:
            column_names = ['Avg Quality', 'Comment Count']
        
        video_stats = df.groupby('title').agg(agg_dict).round(2)
        video_stats.columns = column_names
        video_stats = video_stats.sort_values('Avg Quality', ascending=False)
        
        st.dataframe(video_stats.head(10), use_container_width=True)

def insights_page():
    st.header("🤖 AI-Powered Insights & Assistant")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    # Initialize AI Assistant
    ai_assistant = AIAssistant(df)
    
    # AI Executive Summary
    st.subheader("📋 AI Executive Summary")
    with st.container():
        summary = ai_assistant.generate_ai_summary()
        st.markdown(summary)
    
    # Tabs for different AI features
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Advanced Insights", "🤖 AI Assistant", "📊 Deep Analysis", "💡 Recommendations"])
    
    with tab1:
        st.subheader("🧠 AI-Generated Advanced Insights")
        
        try:
            # Generate advanced AI insights
            ai_insights = ai_assistant.generate_advanced_insights()
            
            if ai_insights:
                for i, insight in enumerate(ai_insights, 1):
                    st.markdown(f"""
                    <div class="insight-box">
                        <strong>{i}.</strong> {insight}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specific insights generated. Try with a larger dataset.")
            
        except Exception as e:
            st.error(f"Error generating AI insights: {e}")
    
    with tab2:
        st.subheader("💬 AI Assistant - Ask Me Anything!")
        
        # Chat interface
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            with st.container():
                st.markdown(f"**🙋 You:** {question}")
                st.markdown(f"**🤖 AI Assistant:** {answer}")
                st.markdown("---")
        
        # Question input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_question = st.text_input(
                "Ask me about your comment analysis:",
                placeholder="e.g., What's my spam rate? How can I improve engagement? What are the trends?",
                key="ai_question_input"
            )
        
        with col2:
            ask_button = st.button("Ask AI", type="primary")
        
        # Suggested questions
        st.write("**💡 Suggested Questions:**")
        suggested_questions = [
            "What's my spam rate and how can I improve it?",
            "How is my audience sentiment?",
            "What type of engagement do I get most?",
            "What are my content performance insights?",
            "Give me recommendations to improve engagement",
            "What trends do you see in my comments?",
            "How does my comment quality score look?",
            "What should I focus on for my next video?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(suggested_questions):
            col = cols[i % 2]
            if col.button(f"💭 {question}", key=f"suggested_{i}"):
                user_question = question
                ask_button = True
        
        # Process question
        if ask_button and user_question:
            with st.spinner("🤖 AI is thinking..."):
                try:
                    answer = ai_assistant.answer_question(user_question)
                    st.session_state.chat_history.append((user_question, answer))
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Assistant error: {e}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    with tab3:
        st.subheader("📊 Deep Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Top Performing Content Themes**")
            
            # Extract topics from genuine comments
            try:
                from src.analysis import CommentAnalyzer
                analyzer = CommentAnalyzer()
                
                genuine_comments = df[df['relevance'] == 'genuine']['textOriginal_cleaned'].dropna().tolist()
                
                if genuine_comments:
                    topics = analyzer.extract_topics(genuine_comments, n_topics=10)
                    
                    for i, topic in enumerate(topics, 1):
                        st.write(f"{i}. **{topic}**")
                else:
                    st.write("No genuine comments found for topic extraction")
                    
            except Exception as e:
                st.warning(f"Could not extract topics: {e}")
            
            # Engagement quality breakdown
            st.write("**📈 Engagement Quality Breakdown**")
            if 'quality_score' in df.columns:
                quality_ranges = {
                    'Excellent (4-5)': (df['quality_score'] >= 4).sum(),
                    'Good (3-4)': ((df['quality_score'] >= 3) & (df['quality_score'] < 4)).sum(),
                    'Average (2-3)': ((df['quality_score'] >= 2) & (df['quality_score'] < 3)).sum(),
                    'Poor (0-2)': (df['quality_score'] < 2).sum()
                }
                
                for range_name, count in quality_ranges.items():
                    percentage = (count / len(df)) * 100
                    st.write(f"• {range_name}: {count:,} comments ({percentage:.1f}%)")
        
        with col2:
            st.write("**🎭 Sentiment Deep Dive**")
            
            if 'vader_sentiment' in df.columns:
                sentiment_stats = df.groupby('vader_sentiment').agg({
                    'quality_score': 'mean',
                    'textOriginal_cleaned': 'count'
                }).round(2)
                
                sentiment_stats.columns = ['Avg Quality', 'Count']
                st.dataframe(sentiment_stats)
            
            # Time-based analysis if available
            if 'publishedAt' in df.columns:
                st.write("**⏰ Temporal Patterns**")
                try:
                    df['hour'] = pd.to_datetime(df['publishedAt']).dt.hour
                    hourly_engagement = df.groupby('hour')['quality_score'].mean().sort_values(ascending=False)
                    
                    st.write("**Best engagement hours:**")
                    for hour, score in hourly_engagement.head(3).items():
                        st.write(f"• {hour}:00 - Quality Score: {score:.2f}")
                        
                except Exception as e:
                    st.write("Could not analyze temporal patterns")
    
    with tab4:
        st.subheader("💡 AI Recommendations")
        
        # Generate personalized recommendations
        recommendations = ai_assistant._generate_recommendations()
        
        if recommendations:
            st.write("**🎯 Personalized Action Items:**")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"""
                <div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; margin: 1rem 0;">
                    <strong>{i}.</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
        
        # Performance benchmarks
        st.write("**📊 Performance Benchmarks:**")
        
        benchmarks = {
            "Spam Rate": {"current": (df['is_spam'] == True).mean() * 100, "good": "<5%", "excellent": "<2%"},
            "Quality Score": {"current": df['quality_score'].mean(), "good": ">3.0", "excellent": ">4.0"},
            "Positive Sentiment": {"current": (df['vader_sentiment'] == 'positive').mean() * 100, "good": ">50%", "excellent": ">70%"},
            "Genuine Engagement": {"current": (df['relevance'] == 'genuine').mean() * 100, "good": ">60%", "excellent": ">80%"}
        }
        
        for metric, data in benchmarks.items():
            current = data["current"]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(metric, f"{current:.1f}{'%' if 'Rate' in metric or 'Sentiment' in metric or 'Engagement' in metric else ''}")
            with col2:
                st.write(f"Good: {data['good']}")
            with col3:
                st.write(f"Excellent: {data['excellent']}")
            with col4:
                # Status indicator
                if metric == "Spam Rate":
                    status = "🟢 Excellent" if current < 2 else "🟡 Good" if current < 5 else "🔴 Needs Work"
                elif metric == "Quality Score":
                    status = "🟢 Excellent" if current > 4 else "🟡 Good" if current > 3 else "🔴 Needs Work"
                else:
                    status = "🟢 Excellent" if current > 70 else "🟡 Good" if current > 50 else "🔴 Needs Work"
                st.write(status)

def export_page():
    st.header("📋 Data Export")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    st.subheader("💾 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📄 Download Full Results (CSV)",
            data=csv_data,
            file_name=f"loreal_comment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Summary Report
        try:
            dashboard = CommentDashboard(df)
            insights = dashboard.generate_insights()
            
            # Generate summary report
            total_comments = len(df)
            spam_rate = (df['is_spam'] == True).mean() * 100
            avg_quality = df['quality_score'].mean()
            
            sentiment_dist = df['vader_sentiment'].value_counts(normalize=True) * 100
            relevance_dist = df['relevance'].value_counts(normalize=True) * 100
            
            report = f"""L'ORÉAL YOUTUBE COMMENT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===============================================

OVERVIEW
--------
Total Comments: {total_comments:,}
Average Quality Score: {avg_quality:.2f}/5
Spam Rate: {spam_rate:.1f}%

RELEVANCE BREAKDOWN
------------------
"""
            
            for category, percentage in relevance_dist.items():
                report += f"{category.title()}: {percentage:.1f}%\n"
            
            report += "\nSENTIMENT ANALYSIS\n-----------------\n"
            
            for sentiment, percentage in sentiment_dist.items():
                report += f"{sentiment.title()}: {percentage:.1f}%\n"
            
            report += "\nKEY INSIGHTS\n-----------\n"
            
            for insight in insights:
                report += f"• {insight}\n"
            
            st.download_button(
                label="📊 Download Summary Report (TXT)",
                data=report,
                file_name=f"loreal_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error generating report: {e}")
    
    # Data preview
    st.subheader("👀 Data Preview")
    
    # Show column selection
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to preview:",
        all_columns,
        default=['textOriginal_cleaned', 'relevance', 'vader_sentiment', 'engagement_type', 'quality_score'][:5]
    )
    
    if selected_columns:
        st.dataframe(df[selected_columns].head(20), use_container_width=True)
    
    # Statistics
    st.subheader("📈 Quick Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Relevance Distribution**")
        st.write(df['relevance'].value_counts())
    
    with col2:
        st.write("**Sentiment Distribution**")
        st.write(df['vader_sentiment'].value_counts())
    
    with col3:
        st.write("**Engagement Types**")
        st.write(df['engagement_type'].value_counts().head())

if __name__ == "__main__":
    main()