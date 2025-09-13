"""
Main script for L'Oréal YouTube Comment Quality Analysis
"""
import pandas as pd
import os
import sys

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processing import DataProcessor
from src.analysis import CommentAnalyzer
from src.dashboard import CommentDashboard

def main():
    print("🎯 L'Oréal YouTube Comment Quality Analysis")
    print("=" * 50)
    
    # Create data directory if it doesn't exist
    os.makedirs("../data", exist_ok=True)
    os.makedirs("../results", exist_ok=True)
    
    # Step 1: Data Processing
    print("\n📊 Step 1: Loading and Processing Data")
    processor = DataProcessor()
    
    # Check if data files exist
    if not os.path.exists("data/comments.csv") or not os.path.exists("data/videos.csv"):
        print("❌ Data files not found!")
        print("Please place your CSV files in the 'data' directory:")
        print("- data/comments.csv")
        print("- data/videos.csv")
        return
    
    # Load and process data
    if processor.load_datasets():
        if processor.merge_datasets():
            if processor.preprocess_data():
                processor.save_processed_data()
                print("✅ Data processing complete!")
                
                # Print data summary
                summary = processor.get_data_summary()
                print(f"\n📈 Data Summary:")
                print(f"Total comments: {summary['total_comments']:,}")
                print(f"Unique videos: {summary['unique_videos']:,}")
                print(f"Average comment length: {summary['avg_comment_length']:.1f} characters")
                print(f"Top languages: {dict(list(summary['languages'].items())[:3])}")
            else:
                print("❌ Data preprocessing failed")
                return
        else:
            print("❌ Data merging failed")
            return
    else:
        print("❌ Data loading failed")
        return
    
    # Step 2: Comment Analysis
    print("\n🔍 Step 2: Analyzing Comments")
    analyzer = CommentAnalyzer()
    
    # Load processed data
    df = pd.read_csv("data/merged_comments.csv")
    
    # Analyze comments in batches for better performance
    batch_size = 1000
    all_results = []
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(df)-1)//batch_size + 1}")
        
        batch_results = analyzer.analyze_comment_batch(batch)
        all_results.append(batch_results)
    
    # Combine all results
    analysis_df = pd.concat(all_results, ignore_index=True)
    
    # Add quality scores
    quality_scores = []
    for _, row in analysis_df.iterrows():
        original_row = df.iloc[row['comment_id']]
        like_count = original_row.get('likeCount', 0)
        
        quality_score = analyzer.generate_quality_score(
            row['relevance'], 
            row['vader_sentiment'], 
            row['engagement_type'],
            like_count
        )
        quality_scores.append(quality_score)
    
    analysis_df['quality_score'] = quality_scores
    
    # Merge with original data
    final_df = df.merge(analysis_df, left_index=True, right_on='comment_id', how='left')
    
    print("✅ Comment analysis complete!")
    
    # Step 3: Generate Dashboard and Insights
    print("\n📊 Step 3: Generating Dashboard and Insights")
    dashboard = CommentDashboard(final_df)
    
    # Generate insights
    insights = dashboard.generate_insights()
    print("\n🎯 Key Insights:")
    for insight in insights:
        print(f"  {insight}")
    
    # Save results
    final_df.to_csv("results/analyzed_comments.csv", index=False)
    
    # Create visualizations
    try:
        import matplotlib.pyplot as plt
        
        # Generate static plots
        relevance_fig = dashboard.plot_relevance_distribution()
        if relevance_fig:
            relevance_fig.savefig("results/relevance_distribution.png", dpi=300, bbox_inches='tight')
        
        sentiment_fig = dashboard.plot_sentiment_analysis()
        if sentiment_fig:
            sentiment_fig.savefig("results/sentiment_analysis.png", dpi=300, bbox_inches='tight')
        
        engagement_fig = dashboard.plot_engagement_types()
        if engagement_fig:
            engagement_fig.savefig("results/engagement_types.png", dpi=300, bbox_inches='tight')
        
        quality_fig = dashboard.plot_quality_vs_likes()
        if quality_fig:
            quality_fig.savefig("results/quality_vs_likes.png", dpi=300, bbox_inches='tight')
        
        print("✅ Visualizations saved to 'results' directory")
        
    except ImportError:
        print("⚠️ Matplotlib not available - skipping static visualizations")
    
    # Generate summary report
    print("\n📝 Generating Summary Report")
    
    # Calculate key metrics
    total_comments = len(final_df)
    spam_rate = (final_df['is_spam'] == True).mean() * 100
    avg_quality = final_df['quality_score'].mean()
    
    sentiment_dist = final_df['vader_sentiment'].value_counts(normalize=True) * 100
    relevance_dist = final_df['relevance'].value_counts(normalize=True) * 100
    engagement_dist = final_df['engagement_type'].value_counts(normalize=True) * 100
    
    # Extract top topics
    genuine_comments = final_df[final_df['relevance'] == 'genuine']['textOriginal_cleaned'].dropna().tolist()
    top_topics = analyzer.extract_topics(genuine_comments, n_topics=10)
    
    # Create summary report
    report = f"""
L'ORÉAL YOUTUBE COMMENT QUALITY ANALYSIS REPORT
===============================================

OVERVIEW
--------
Total Comments Analyzed: {total_comments:,}
Average Quality Score: {avg_quality:.2f}/5
Spam Rate: {spam_rate:.1f}%

RELEVANCE BREAKDOWN
------------------
"""
    
    for category, percentage in relevance_dist.items():
        report += f"{category.title()}: {percentage:.1f}%\n"
    
    report += f"""
SENTIMENT ANALYSIS
-----------------
"""
    
    for sentiment, percentage in sentiment_dist.items():
        report += f"{sentiment.title()}: {percentage:.1f}%\n"
    
    report += f"""
TOP ENGAGEMENT TYPES
-------------------
"""
    
    for eng_type, percentage in engagement_dist.head().items():
        report += f"{eng_type.title()}: {percentage:.1f}%\n"
    
    if top_topics:
        report += f"""
TOP DISCUSSION TOPICS
--------------------
"""
        for i, topic in enumerate(top_topics, 1):
            report += f"{i}. {topic}\n"
    
    report += f"""
KEY INSIGHTS
-----------
"""
    
    for insight in insights:
        report += f"• {insight}\n"
    
    report += f"""
RECOMMENDATIONS
--------------
• Focus on content that generates genuine engagement (questions, technique requests)
• Monitor and moderate spam comments to maintain community quality
• Leverage positive sentiment by encouraging more user-generated content
• Create content addressing top discussion topics and frequently asked questions
• Consider implementing comment quality scoring for better community management

Generated by Kiro AI Assistant
"""
    
    # Save report
    with open("results/analysis_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("✅ Analysis complete!")
    print(f"\n📁 Results saved to:")
    print(f"  - results/analyzed_comments.csv")
    print(f"  - results/analysis_report.txt")
    print(f"  - results/*.png (visualizations)")
    
    print(f"\n🎉 L'Oréal Comment Quality Analysis Complete!")

if __name__ == "__main__":
    main()