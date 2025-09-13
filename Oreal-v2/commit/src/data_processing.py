"""
Data loading, cleaning, and merging for YouTube comment analysis
"""
import pandas as pd
import numpy as np
import re
from textblob import TextBlob
from langdetect import detect, DetectorFactory
import emoji

# Set seed for consistent language detection
DetectorFactory.seed = 0

class DataProcessor:
    def __init__(self):
        self.comments_df = None
        self.videos_df = None
        self.merged_df = None
    
    def load_datasets(self, comments_path="data/comments.csv", videos_path="data/videos.csv"):
        """Load comments and videos datasets"""
        try:
            print("Loading datasets...")
            self.comments_df = pd.read_csv(comments_path, encoding='utf-8')
            self.videos_df = pd.read_csv(videos_path, encoding='utf-8')
            
            print(f"Comments loaded: {len(self.comments_df)} rows")
            print(f"Videos loaded: {len(self.videos_df)} rows")
            
            return True
        except Exception as e:
            print(f"Error loading datasets: {e}")
            return False
    
    def merge_datasets(self):
        """Merge comments with video metadata"""
        if self.comments_df is None or self.videos_df is None:
            print("Please load datasets first")
            return False
        
        print("Merging datasets...")
        
        # Fill NaN values before merging
        self.comments_df = self.comments_df.fillna('')
        self.videos_df = self.videos_df.fillna('')
        
        self.merged_df = pd.merge(
            self.comments_df, 
            self.videos_df, 
            on="videoId", 
            how="left"
        )
        
        # Fill any remaining NaN values after merge
        self.merged_df = self.merged_df.fillna('')
        
        print(f"Merged dataset: {len(self.merged_df)} rows")
        return True
    
    def clean_text(self, text):
        """Clean and normalize comment text"""
        if pd.isna(text) or text is None:
            return ""
        
        # Convert to string and handle various null-like values
        text = str(text)
        if text.lower() in ['nan', 'none', 'null', '']:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Convert emojis to text descriptions (optional)
        # text = emoji.demojize(text)
        
        return text
    
    def detect_language(self, text):
        """Detect comment language"""
        try:
            if len(text.strip()) < 3:
                return "unknown"
            return detect(text)
        except:
            return "unknown"
    
    def preprocess_data(self):
        """Clean and preprocess the merged dataset"""
        if self.merged_df is None:
            print("Please merge datasets first")
            return False
        
        print(f"Preprocessing {len(self.merged_df):,} comments...")
        
        # Clean text efficiently
        print("Cleaning text...")
        self.merged_df['textOriginal_cleaned'] = self.merged_df['textOriginal'].apply(self.clean_text)
        
        # Detect language for sample only if dataset is large
        if len(self.merged_df) > 10000:
            print("Detecting languages (sampling for large dataset)...")
            # Sample for language detection to speed up processing
            sample_size = min(5000, len(self.merged_df))
            sample_indices = self.merged_df.sample(n=sample_size, random_state=42).index
            
            # Detect language for sample
            sample_languages = self.merged_df.loc[sample_indices, 'textOriginal_cleaned'].apply(self.detect_language)
            
            # Use most common language for all
            most_common_lang = sample_languages.mode().iloc[0] if not sample_languages.empty else 'en'
            self.merged_df['detected_language'] = most_common_lang
            print(f"Using detected language: {most_common_lang} (based on sample)")
        else:
            print("Detecting languages...")
            self.merged_df['detected_language'] = self.merged_df['textOriginal_cleaned'].apply(self.detect_language)
        
        # Add basic text features efficiently
        print("Adding text features...")
        self.merged_df['comment_length'] = self.merged_df['textOriginal_cleaned'].str.len()
        self.merged_df['word_count'] = self.merged_df['textOriginal_cleaned'].str.split().str.len()
        
        # Handle missing values
        numeric_columns = ['likeCount', 'replyCount']
        for col in numeric_columns:
            if col in self.merged_df.columns:
                self.merged_df[col] = pd.to_numeric(self.merged_df[col], errors='coerce').fillna(0)
        
        print("Preprocessing complete!")
        return True
    
    def save_processed_data(self, output_path="data/merged_comments.csv"):
        """Save the processed dataset"""
        if self.merged_df is None:
            print("No processed data to save")
            return False
        
        self.merged_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Processed data saved to {output_path}")
        return True
    
    def get_data_summary(self):
        """Get summary statistics of the processed data"""
        if self.merged_df is None:
            return "No data loaded"
        
        summary = {
            'total_comments': len(self.merged_df),
            'unique_videos': self.merged_df['videoId'].nunique(),
            'languages': self.merged_df['detected_language'].value_counts().to_dict(),
            'avg_comment_length': self.merged_df['comment_length'].mean(),
            'avg_word_count': self.merged_df['word_count'].mean(),
            'total_likes': self.merged_df['likeCount'].sum() if 'likeCount' in self.merged_df.columns else 0
        }
        
        return summary

if __name__ == "__main__":
    # Example usage
    processor = DataProcessor()
    
    if processor.load_datasets():
        if processor.merge_datasets():
            if processor.preprocess_data():
                processor.save_processed_data()
                print("\nData Summary:")
                summary = processor.get_data_summary()
                for key, value in summary.items():
                    print(f"{key}: {value}")