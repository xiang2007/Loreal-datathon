"""
Configuration file for YouTube comment analysis
"""

# Quality scoring weights
QUALITY_WEIGHTS = {
    'relevance': {
        'genuine': 3,
        'general': 1,
        'spam': -2
    },
    'engagement': {
        'question': 2,
        'suggestion': 2,
        'technique_request': 3,
        'praise': 1,
        'thanks': 1,
        'general': 0
    },
    'sentiment_bonus': 1,  # Bonus for positive/neutral sentiment
    'like_bonus_cap': 2    # Maximum bonus points from likes
}

# Spam detection thresholds
SPAM_CONFIG = {
    'min_comment_length': 3,
    'min_unique_words': 2,
    'spam_score_threshold': 2,
    'patterns': {
        'self_promotion': r'(check out|visit|subscribe|follow|link in bio|dm me)',
        'excessive_emojis': r'[😀-🿿]{5,}',
        'repeated_chars': r'(.)\1{4,}',
        'caps_spam': r'^[A-Z\s!]{10,}$',
        'url_pattern': r'http[s]?://|www\.|\.com|\.org',
        'generic_praise': r'^(nice|good|great|amazing|love it|beautiful)!*$'
    }
}

# Engagement type patterns
ENGAGEMENT_PATTERNS = {
    'question': r'\?|how to|what|where|when|why|which|can you',
    'suggestion': r'should|could|try|suggest|recommend|maybe|perhaps',
    'praise': r'love|amazing|beautiful|gorgeous|perfect|stunning|incredible',
    'thanks': r'thank|thanks|grateful|appreciate',
    'technique_request': r'tutorial|how to|teach|show|explain|steps'
}

# Relevance classification
RELEVANCE_CONFIG = {
    'word_overlap_threshold': 0.2,  # 20% word overlap for genuine classification
    'use_video_context': True
}

# Sentiment analysis
SENTIMENT_CONFIG = {
    'use_vader': True,
    'use_textblob': True,
    'vader_thresholds': {
        'positive': 0.05,
        'negative': -0.05
    },
    'textblob_thresholds': {
        'positive': 0.1,
        'negative': -0.1
    }
}

# Topic extraction
TOPIC_CONFIG = {
    'max_features': 100,
    'min_df': 2,
    'ngram_range': (1, 2),
    'stop_words': 'english',
    'n_topics': 10
}

# Dashboard settings
DASHBOARD_CONFIG = {
    'figure_size': (12, 8),
    'color_palette': {
        'genuine': '#2E8B57',
        'general': '#4682B4', 
        'spam': '#DC143C',
        'positive': '#32CD32',
        'neutral': '#FFD700',
        'negative': '#FF6347'
    },
    'save_plots': True,
    'plot_dpi': 300
}

# File paths
PATHS = {
    'data_dir': 'data',
    'results_dir': 'results',
    'comments_file': 'comments.csv',
    'videos_file': 'videos.csv',
    'merged_file': 'merged_comments.csv',
    'analyzed_file': 'analyzed_comments.csv',
    'report_file': 'analysis_report.txt'
}

# Processing settings
PROCESSING_CONFIG = {
    'batch_size': 1000,
    'encoding': 'utf-8',
    'random_state': 42,
    'sample_size_for_notebook': 500
}

# Language detection
LANGUAGE_CONFIG = {
    'detect_language': True,
    'min_text_length_for_detection': 3,
    'default_language': 'unknown'
}