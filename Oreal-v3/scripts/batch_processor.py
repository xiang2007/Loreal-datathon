"""
Batch processor for multiple CSV files - Single command execution
"""
import os
import sys
import pandas as pd
import glob
from datetime import datetime
import argparse

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processing import DataProcessor
from src.analysis import CommentAnalyzer
from dashboard import CommentDashboard

class BatchProcessor:
    def __init__(self, input_dir="batch_input", output_dir="batch_output"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.results = []
        
        # Create directories if they don't exist
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
    
    def find_csv_files(self):
        """Find all CSV files in input directory"""
        csv_files = glob.glob(os.path.join(self.input_dir, "*.csv"))
        
        # Separate comments and videos files
        comments_files = []
        videos_files = []
        
        for file in csv_files:
            filename = os.path.basename(file).lower()
            if 'comment' in filename:
                comments_files.append(file)
            elif 'video' in filename:
                videos_files.append(file)
            else:
                # Try to detect by content
                try:
                    df = pd.read_csv(file, nrows=1)
                    if 'textOriginal' in df.columns:
                        comments_files.append(file)
                    elif 'title' in df.columns:
                        videos_files.append(file)
                except:
                    print(f"⚠️ Could not process file: {file}")
        
        return comments_files, videos_files
    
    def auto_match_files(self, comments_files, videos_files):
        """Automatically match comments and videos files"""
        pairs = []
        
        for comment_file in comments_files:
            comment_base = os.path.basename(comment_file)
            best_match = None
            
            # Try to find matching video file
            for video_file in videos_files:
                video_base = os.path.basename(video_file)
                
                # Simple matching logic
                comment_name = comment_base.replace('comment', '').replace('.csv', '')
                video_name = video_base.replace('video', '').replace('.csv', '')
                
                if comment_name == video_name or comment_name in video_name or video_name in comment_name:
                    best_match = video_file
                    break
            
            if best_match:
                pairs.append((comment_file, best_match))
                videos_files.remove(best_match)  # Remove to avoid duplicate matching
            else:
                # Use first available video file as fallback
                if videos_files:
                    pairs.append((comment_file, videos_files[0]))
                else:
                    pairs.append((comment_file, None))
        
        return pairs
    
    def process_file_pair(self, comments_file, videos_file, pair_name):
        """Process a single pair of files"""
        print(f"\n🔄 Processing: {pair_name}")
        print(f"Comments: {os.path.basename(comments_file)}")
        print(f"Videos: {os.path.basename(videos_file) if videos_file else 'None'}")
        
        try:
            # Load data
            processor = DataProcessor()
            
            comments_df = pd.read_csv(comments_file)
            if videos_file:
                videos_df = pd.read_csv(videos_file)
            else:
                # Create dummy videos dataframe
                unique_videos = comments_df['videoId'].unique()
                videos_df = pd.DataFrame({
                    'videoId': unique_videos,
                    'title': [f'Video {i}' for i in range(len(unique_videos))],
                    'description': [''] * len(unique_videos)
                })
            
            processor.comments_df = comments_df
            processor.videos_df = videos_df
            
            # Process data
            if not processor.merge_datasets():
                raise Exception("Failed to merge datasets")
            
            if not processor.preprocess_data():
                raise Exception("Failed to preprocess data")
            
            # Analyze comments
            analyzer = CommentAnalyzer()
            
            # Process in batches for large datasets
            batch_size = 1000 if len(processor.merged_df) > 10000 else 500
            all_results = []
            
            total_batches = (len(processor.merged_df) - 1) // batch_size + 1
            
            for i in range(0, len(processor.merged_df), batch_size):
                batch_num = (i // batch_size) + 1
                print(f"  Processing batch {batch_num}/{total_batches}...")
                
                batch = processor.merged_df.iloc[i:i+batch_size]
                batch_results = analyzer.analyze_comment_batch(batch)
                all_results.append(batch_results)
            
            # Combine results
            analysis_df = pd.concat(all_results, ignore_index=True)
            
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
            
            # Save results
            output_file = os.path.join(self.output_dir, f"{pair_name}_analyzed.csv")
            final_df.to_csv(output_file, index=False)
            
            # Generate insights
            dashboard = CommentDashboard(final_df)
            insights = dashboard.generate_insights()
            
            # Save report
            report_file = os.path.join(self.output_dir, f"{pair_name}_report.txt")
            self.generate_report(final_df, insights, report_file, pair_name)
            
            # Store results summary
            result_summary = {
                'name': pair_name,
                'total_comments': len(final_df),
                'spam_rate': (final_df['is_spam'] == True).mean() * 100,
                'avg_quality': final_df['quality_score'].mean(),
                'positive_sentiment': (final_df['vader_sentiment'] == 'positive').mean() * 100,
                'output_file': output_file,
                'report_file': report_file,
                'status': 'Success'
            }
            
            self.results.append(result_summary)
            print(f"✅ {pair_name} processed successfully!")
            
        except Exception as e:
            print(f"❌ Error processing {pair_name}: {e}")
            self.results.append({
                'name': pair_name,
                'status': 'Failed',
                'error': str(e)
            })
    
    def generate_report(self, df, insights, report_file, pair_name):
        """Generate analysis report for a file pair"""
        total_comments = len(df)
        spam_rate = (df['is_spam'] == True).mean() * 100
        avg_quality = df['quality_score'].mean()
        
        sentiment_dist = df['vader_sentiment'].value_counts(normalize=True) * 100
        relevance_dist = df['relevance'].value_counts(normalize=True) * 100
        engagement_dist = df['engagement_type'].value_counts(normalize=True) * 100
        
        report = f"""L'ORÉAL YOUTUBE COMMENT ANALYSIS REPORT
Dataset: {pair_name}
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
        
        report += "\nTOP ENGAGEMENT TYPES\n-------------------\n"
        
        for eng_type, percentage in engagement_dist.head().items():
            report += f"{eng_type.title()}: {percentage:.1f}%\n"
        
        report += "\nKEY INSIGHTS\n-----------\n"
        
        for insight in insights:
            report += f"• {insight}\n"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
    
    def generate_summary_report(self):
        """Generate overall summary report"""
        summary_file = os.path.join(self.output_dir, "batch_summary.txt")
        
        successful = [r for r in self.results if r['status'] == 'Success']
        failed = [r for r in self.results if r['status'] == 'Failed']
        
        summary = f"""BATCH PROCESSING SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================

OVERVIEW
--------
Total Files Processed: {len(self.results)}
Successful: {len(successful)}
Failed: {len(failed)}

"""
        
        if successful:
            summary += "SUCCESSFUL ANALYSES\n------------------\n"
            for result in successful:
                summary += f"""
Dataset: {result['name']}
- Comments: {result['total_comments']:,}
- Spam Rate: {result['spam_rate']:.1f}%
- Avg Quality: {result['avg_quality']:.2f}/5
- Positive Sentiment: {result['positive_sentiment']:.1f}%
- Output: {os.path.basename(result['output_file'])}
- Report: {os.path.basename(result['report_file'])}
"""
        
        if failed:
            summary += "\nFAILED ANALYSES\n--------------\n"
            for result in failed:
                summary += f"- {result['name']}: {result.get('error', 'Unknown error')}\n"
        
        summary += f"\nAll results saved to: {self.output_dir}\n"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary_file
    
    def run_batch_processing(self):
        """Run complete batch processing"""
        print("🚀 L'Oréal Comment Analysis - Batch Processor")
        print("=" * 50)
        
        # Find CSV files
        comments_files, videos_files = self.find_csv_files()
        
        if not comments_files:
            print(f"❌ No comment files found in {self.input_dir}")
            print("Please place your CSV files in the batch_input directory")
            print("Files should contain 'comment' in the name or have 'textOriginal' column")
            return
        
        print(f"📁 Found {len(comments_files)} comment files and {len(videos_files)} video files")
        
        # Match files
        file_pairs = self.auto_match_files(comments_files, videos_files)
        
        print(f"🔗 Created {len(file_pairs)} file pairs for processing")
        
        # Process each pair
        for i, (comment_file, video_file) in enumerate(file_pairs, 1):
            pair_name = f"dataset_{i:02d}"
            self.process_file_pair(comment_file, video_file, pair_name)
        
        # Generate summary
        summary_file = self.generate_summary_report()
        
        print(f"\n🎉 Batch processing complete!")
        print(f"📊 Summary report: {summary_file}")
        print(f"📁 All results saved to: {self.output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Batch process multiple CSV files')
    parser.add_argument('--input', '-i', default='batch_input', 
                       help='Input directory containing CSV files (default: batch_input)')
    parser.add_argument('--output', '-o', default='batch_output',
                       help='Output directory for results (default: batch_output)')
    
    args = parser.parse_args()
    
    processor = BatchProcessor(args.input, args.output)
    processor.run_batch_processing()

if __name__ == "__main__":
    main()