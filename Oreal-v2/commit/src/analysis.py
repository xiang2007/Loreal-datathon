"""
Comment analysis and classification module
"""
import pandas as pd
import numpy as np
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CommentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.spam_patterns = self._compile_spam_patterns()
        self.engagement_patterns = self._compile_engagement_patterns()
    
    def _compile_spam_patterns(self):
        """Compile regex patterns for spam detection"""
        patterns = {
            'self_promotion': re.compile(r'(check out|visit|subscribe|follow|link in bio|dm me)', re.IGNORECASE),
            'excessive_emojis': re.compile(r'[😀-🿿]{5,}'),  # 5+ consecutive emojis
            'repeated_chars': re.compile(r'(.)\1{4,}'),  # Same character 5+ times
            'caps_spam': re.compile(r'^[A-Z\s!]{10,}$'),  # All caps messages
            'url_pattern': re.compile(r'http[s]?://|www\.|\.com|\.org'),
            'generic_praise': re.compile(r'^(nice|good|great|amazing|love it|beautiful)!*$', re.IGNORECASE)
        }
        return patterns
    
    def _compile_engagement_patterns(self):
        """Compile patterns for engagement type detection"""
        patterns = {
            'question': re.compile(r'\?|how to|what|where|when|why|which|can you', re.IGNORECASE),
            'suggestion': re.compile(r'should|could|try|suggest|recommend|maybe|perhaps', re.IGNORECASE),
            'praise': re.compile(r'love|amazing|beautiful|gorgeous|perfect|stunning|incredible', re.IGNORECASE),
            'thanks': re.compile(r'thank|thanks|grateful|appreciate', re.IGNORECASE),
            'technique_request': re.compile(r'tutorial|how to|teach|show|explain|steps', re.IGNORECASE)
        }
        return patterns
    
    def detect_spam(self, text):
        """Detect if comment is likely spam"""
        if not text or len(text.strip()) < 3:
            return True
        
        spam_score = 0
        
        # Check each spam pattern
        for pattern_name, pattern in self.spam_patterns.items():
            if pattern.search(text):
                spam_score += 1
        
        # Additional spam indicators
        if len(text) < 5:  # Very short comments
            spam_score += 1
        
        if len(set(text.lower().split())) < 2:  # Very few unique words
            spam_score += 1
        
        return spam_score >= 2  # Threshold for spam classification
    
    def classify_relevance(self, comment_text, video_title="", video_description=""):
        """Classify comment relevance to video content"""
        if self.detect_spam(comment_text):
            return "spam"
        
        # Handle NaN values from pandas
        video_title = str(video_title) if video_title and str(video_title) != 'nan' else ""
        video_description = str(video_description) if video_description and str(video_description) != 'nan' else ""
        
        if not video_title and not video_description:
            return "general"  # Can't determine relevance without video context
        
        # Simple keyword matching approach
        comment_words = set(comment_text.lower().split())
        video_words = set((video_title + " " + video_description).lower().split())
        
        # Calculate word overlap
        overlap = len(comment_words.intersection(video_words))
        overlap_ratio = overlap / len(comment_words) if comment_words else 0
        
        if overlap_ratio > 0.2:  # 20% word overlap threshold
            return "genuine"
        else:
            return "general"
    
    def analyze_sentiment_vader(self, text):
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        
        # Classify based on compound score
        if scores['compound'] >= 0.05:
            return 'positive', scores['compound']
        elif scores['compound'] <= -0.05:
            return 'negative', scores['compound']
        else:
            return 'neutral', scores['compound']
    
    def analyze_sentiment_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive', polarity
        elif polarity < -0.1:
            return 'negative', polarity
        else:
            return 'neutral', polarity
    
    def classify_engagement_type(self, text):
        """Classify the type of engagement"""
        engagement_scores = {}
        
        for eng_type, pattern in self.engagement_patterns.items():
            matches = len(pattern.findall(text))
            engagement_scores[eng_type] = matches
        
        # Return the engagement type with highest score
        if max(engagement_scores.values()) > 0:
            return max(engagement_scores, key=engagement_scores.get)
        else:
            return 'general'
    
    def extract_topics(self, comments_list, n_topics=5):
        """Extract main topics from comments using TF-IDF"""
        # Clean and filter comments
        clean_comments = [c for c in comments_list if c and len(c.strip()) > 10]
        
        if len(clean_comments) < 2:
            return []
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(clean_comments)
            feature_names = vectorizer.get_feature_names_out()
            
            # Get top terms
            mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
            top_indices = mean_scores.argsort()[-n_topics:][::-1]
            
            topics = [feature_names[i] for i in top_indices]
            return topics
        except:
            return []
    
    def analyze_comment_batch(self, df):
        """Analyze a batch of comments with optimized processing"""
        results = []
        
        # Pre-extract data to avoid repeated lookups
        comments_data = []
        for idx, row in df.iterrows():
            comment_text = row.get('textOriginal_cleaned', '')
            if comment_text and len(comment_text.strip()) > 0:  # Skip empty comments
                # Handle NaN values properly
                video_title = row.get('title', '')
                video_description = row.get('description', '')
                
                # Convert NaN to empty string
                if pd.isna(video_title):
                    video_title = ''
                if pd.isna(video_description):
                    video_description = ''
                
                comments_data.append({
                    'idx': idx,
                    'text': comment_text,
                    'video_title': str(video_title),
                    'video_description': str(video_description)
                })
        
        # Process comments efficiently
        for data in comments_data:
            comment_text = data['text']
            
            # Ensure video data is properly handled
            video_title = data.get('video_title', '')
            video_description = data.get('video_description', '')
            
            # Core analysis
            analysis = {
                'comment_id': data['idx'],
                'relevance': self.classify_relevance(comment_text, video_title, video_description),
                'engagement_type': self.classify_engagement_type(comment_text),
                'is_spam': self.detect_spam(comment_text)
            }
            
            # Sentiment analysis (use VADER only for speed on large datasets)
            vader_sentiment, vader_score = self.analyze_sentiment_vader(comment_text)
            
            # Only use TextBlob for smaller batches to save time
            if len(comments_data) < 1000:
                textblob_sentiment, textblob_score = self.analyze_sentiment_textblob(comment_text)
            else:
                textblob_sentiment, textblob_score = vader_sentiment, vader_score
            
            analysis.update({
                'vader_sentiment': vader_sentiment,
                'vader_score': vader_score,
                'textblob_sentiment': textblob_sentiment,
                'textblob_score': textblob_score
            })
            
            results.append(analysis)
        
        return pd.DataFrame(results)
    
    def generate_quality_score(self, relevance, sentiment, engagement_type, like_count=0):
        """Generate overall quality score for a comment"""
        score = 0
        
        # Relevance scoring
        relevance_scores = {'genuine': 3, 'general': 1, 'spam': -2}
        score += relevance_scores.get(relevance, 0)
        
        # Engagement scoring
        engagement_scores = {
            'question': 2, 'suggestion': 2, 'technique_request': 3,
            'praise': 1, 'thanks': 1, 'general': 0
        }
        score += engagement_scores.get(engagement_type, 0)
        
        # Sentiment bonus (constructive feedback is valuable)
        if sentiment in ['positive', 'neutral']:
            score += 1
        
        # Like count bonus (logarithmic scale)
        if like_count > 0:
            score += min(np.log10(like_count + 1), 2)  # Cap at 2 points
        
        return max(score, 0)  # Ensure non-negative score

if __name__ == "__main__":
    # Example usage
    analyzer = CommentAnalyzer()
    
    # Test with sample comments
    sample_comments = [
        "Love this makeup tutorial! Can you do one for evening looks?",
        "AMAZING!!! 😍😍😍😍😍",
        "Check out my channel for more beauty tips!",
        "What foundation are you using? It looks so natural",
        "This technique doesn't work for my skin type"
    ]
    
    for comment in sample_comments:
        relevance = analyzer.classify_relevance(comment)
        engagement = analyzer.classify_engagement_type(comment)
        sentiment, score = analyzer.analyze_sentiment_vader(comment)
        is_spam = analyzer.detect_spam(comment)
        quality = analyzer.generate_quality_score(relevance, sentiment, engagement)
        
        print(f"Comment: {comment}")
        print(f"Relevance: {relevance}, Engagement: {engagement}")
        print(f"Sentiment: {sentiment} ({score:.2f}), Spam: {is_spam}")
        print(f"Quality Score: {quality}")
        print("-" * 50)