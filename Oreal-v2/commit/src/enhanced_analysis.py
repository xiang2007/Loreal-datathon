"""
Enhanced comment analysis and classification module with improved spam and engagement detection
"""
import pandas as pd
import numpy as np
import re
import string
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import unicodedata

class EnhancedCommentAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.spam_patterns = self._compile_spam_patterns()
        self.engagement_patterns = self._compile_engagement_patterns()
        self.beauty_categories = self._compile_beauty_categories()
        self.gibberish_threshold = 0.6  # Threshold for gibberish detection
        
    def _compile_spam_patterns(self):
        """Enhanced regex patterns for spam detection"""
        patterns = {
            'self_promotion': re.compile(r'(check out|visit|subscribe|follow|link in bio|dm me|my channel|my video|click here|watch my|see my)', re.IGNORECASE),
            'excessive_emojis': re.compile(r'[😀-🿿]{5,}'),  # 5+ consecutive emojis
            'repeated_chars': re.compile(r'(.)\1{4,}'),  # Same character 5+ times
            'caps_spam': re.compile(r'^[A-Z\s!]{10,}$'),  # All caps messages
            'url_pattern': re.compile(r'http[s]?://|www\.|\.com|\.org|\.net|bit\.ly|tinyurl|youtube\.com|youtu\.be'),
            'generic_praise': re.compile(r'^(nice|good|great|amazing|love it|beautiful|wow|cool|awesome|perfect)!*$', re.IGNORECASE),
            'excessive_punctuation': re.compile(r'[!?.]{4,}'),  # Too much punctuation
            'keyboard_mashing': re.compile(r'(qwerty|asdf|zxcv|hjkl|uiop|qwe|asd|zxc)', re.IGNORECASE),  # Keyboard patterns
            'bot_patterns': re.compile(r'(bot|spam|fake|scam|virus|hack|malware)', re.IGNORECASE),
            'money_spam': re.compile(r'(\$|money|cash|earn|income|profit|investment|bitcoin|crypto)', re.IGNORECASE),
            'contact_spam': re.compile(r'(whatsapp|telegram|email|contact|phone|number|call me|text me)', re.IGNORECASE),
            'random_numbers': re.compile(r'\b\d{5,}\b'),  # Long random numbers
            'excessive_symbols': re.compile(r'[^\w\s]{5,}'),  # Too many symbols
        }
        return patterns
    
    def _compile_engagement_patterns(self):
        """Enhanced patterns for engagement type detection"""
        patterns = {
            'question': re.compile(r'\?|how to|what|where|when|why|which|can you|could you|would you|do you|have you|is it|are you|will you', re.IGNORECASE),
            'suggestion': re.compile(r'should|could|try|suggest|recommend|maybe|perhaps|you might|consider|what about|how about', re.IGNORECASE),
            'praise': re.compile(r'love|amazing|beautiful|gorgeous|perfect|stunning|incredible|fantastic|wonderful|brilliant|excellent|outstanding', re.IGNORECASE),
            'thanks': re.compile(r'thank|thanks|grateful|appreciate|bless|god bless', re.IGNORECASE),
            'technique_request': re.compile(r'tutorial|how to|teach|show|explain|steps|guide|instruction|demo|demonstrate|learn', re.IGNORECASE),
            'product_inquiry': re.compile(r'what.*using|which.*brand|name.*product|where.*buy|link.*product|shade.*name|color.*name', re.IGNORECASE),
            'criticism': re.compile(r'bad|terrible|awful|hate|dislike|wrong|horrible|disgusting|ugly|worst', re.IGNORECASE),
            'personal_story': re.compile(r'i have|i use|i tried|my.*is|when i|i always|i never|i love|i hate', re.IGNORECASE),
            'request_collab': re.compile(r'collab|collaboration|work together|partnership|sponsor|brand deal', re.IGNORECASE),
            'compliment_specific': re.compile(r'your.*beautiful|your.*amazing|your.*perfect|love your|adore your', re.IGNORECASE)
        }
        return patterns
    
    def _compile_beauty_categories(self):
        """Compile comprehensive beauty category patterns for L'Oréal products"""
        categories = {
            'makeup': {
                'keywords': [
                    # Face makeup
                    'foundation', 'concealer', 'primer', 'powder', 'setting spray', 'bb cream', 'cc cream',
                    'tinted moisturizer', 'base', 'coverage', 'full coverage', 'light coverage',
                    
                    # Eye makeup
                    'eyeshadow', 'eyeliner', 'mascara', 'eyebrow', 'brow', 'lashes', 'false lashes',
                    'eye primer', 'eyeshadow palette', 'smoky eye', 'winged liner', 'cat eye',
                    
                    # Lip makeup
                    'lipstick', 'lip gloss', 'lip liner', 'lip balm', 'matte lips', 'liquid lipstick',
                    'lip stain', 'lip color', 'nude lips', 'red lips',
                    
                    # Cheek makeup
                    'blush', 'bronzer', 'highlighter', 'contour', 'contouring', 'cheek color',
                    'glow', 'shimmer', 'matte finish',
                    
                    # Tools and application
                    'makeup brush', 'beauty blender', 'sponge', 'application', 'blend', 'blending'
                ],
                'patterns': [
                    r'makeup.*look', r'makeup.*tutorial', r'makeup.*routine', r'makeup.*tips',
                    r'eye.*makeup', r'face.*makeup', r'lip.*makeup', r'daily.*makeup',
                    r'evening.*makeup', r'natural.*makeup', r'glam.*makeup'
                ]
            },
            
            'skincare': {
                'keywords': [
                    # Skin types and concerns
                    'skincare', 'skin care', 'acne', 'wrinkles', 'aging', 'anti-aging', 'fine lines',
                    'dark spots', 'hyperpigmentation', 'melasma', 'sun damage', 'age spots',
                    'oily skin', 'dry skin', 'sensitive skin', 'combination skin', 'mature skin',
                    'dehydrated', 'dull skin', 'uneven skin tone', 'texture', 'pores',
                    
                    # Products and ingredients
                    'serum', 'moisturizer', 'cleanser', 'toner', 'exfoliant', 'mask', 'face mask',
                    'retinol', 'vitamin c', 'hyaluronic acid', 'niacinamide', 'salicylic acid',
                    'glycolic acid', 'peptides', 'collagen', 'antioxidants', 'spf', 'sunscreen',
                    
                    # Routines and application
                    'skincare routine', 'morning routine', 'night routine', 'double cleansing',
                    'layering', 'skin barrier', 'hydration', 'exfoliation'
                ],
                'patterns': [
                    r'skin.*care', r'skin.*routine', r'skin.*type', r'skin.*concern',
                    r'anti.*aging', r'acne.*treatment', r'wrinkle.*cream', r'face.*serum',
                    r'daily.*skincare', r'skincare.*tips', r'skin.*health'
                ]
            },
            
            'fragrance': {
                'keywords': [
                    # Fragrance types
                    'perfume', 'fragrance', 'cologne', 'eau de parfum', 'eau de toilette',
                    'body spray', 'mist', 'scent', 'smell', 'aroma',
                    
                    # Fragrance families
                    'floral', 'fruity', 'woody', 'oriental', 'fresh', 'citrus', 'musky',
                    'vanilla', 'rose', 'jasmine', 'sandalwood', 'bergamot', 'lavender',
                    
                    # Fragrance characteristics
                    'long lasting', 'sillage', 'projection', 'longevity', 'top notes',
                    'middle notes', 'base notes', 'dry down', 'signature scent'
                ],
                'patterns': [
                    r'perfume.*collection', r'fragrance.*review', r'scent.*of.*the.*day',
                    r'signature.*scent', r'perfume.*recommendation', r'fragrance.*tips'
                ]
            },
            
            'haircare': {
                'keywords': [
                    # Hair types and concerns
                    'hair', 'haircare', 'hair care', 'shampoo', 'conditioner', 'hair mask',
                    'hair oil', 'hair serum', 'dry hair', 'oily hair', 'damaged hair',
                    'frizzy hair', 'curly hair', 'straight hair', 'color treated hair',
                    
                    # Hair styling
                    'hair styling', 'heat protection', 'hair spray', 'mousse', 'gel',
                    'hair color', 'hair dye', 'highlights', 'balayage', 'ombre',
                    
                    # Hair health
                    'hair growth', 'hair loss', 'scalp care', 'dandruff', 'hair strength',
                    'hair repair', 'split ends', 'hair texture'
                ],
                'patterns': [
                    r'hair.*care', r'hair.*routine', r'hair.*treatment', r'hair.*styling',
                    r'hair.*color', r'hair.*health', r'scalp.*care'
                ]
            },
            
            'nails': {
                'keywords': [
                    'nail polish', 'nail care', 'manicure', 'pedicure', 'nail art',
                    'gel nails', 'acrylic nails', 'nail treatment', 'cuticle care',
                    'nail strengthener', 'base coat', 'top coat', 'nail color',
                    'nail design', 'nail health', 'nail growth'
                ],
                'patterns': [
                    r'nail.*polish', r'nail.*art', r'nail.*care', r'nail.*design'
                ]
            },
            
            'tools_accessories': {
                'keywords': [
                    'makeup brush', 'beauty blender', 'sponge', 'mirror', 'tweezers',
                    'eyelash curler', 'makeup bag', 'cosmetic bag', 'beauty tools',
                    'applicator', 'brush set', 'makeup organizer', 'vanity',
                    'lighting', 'magnifying mirror'
                ],
                'patterns': [
                    r'makeup.*tools', r'beauty.*tools', r'makeup.*brush', r'beauty.*accessories'
                ]
            }
        }
        
        # Compile regex patterns for each category
        compiled_categories = {}
        for category, data in categories.items():
            compiled_patterns = []
            
            # Compile keyword patterns
            for keyword in data['keywords']:
                compiled_patterns.append(re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE))
            
            # Compile phrase patterns
            for pattern in data.get('patterns', []):
                compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            
            compiled_categories[category] = compiled_patterns
        
        return compiled_categories
    
    def classify_beauty_category(self, text):
        """Classify comment into beauty categories"""
        if not text or len(text.strip()) < 3:
            return 'general'
        
        text_lower = text.lower()
        category_scores = {}
        
        # Score each category based on keyword matches
        for category, patterns in self.beauty_categories.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(text))
                score += matches
            
            # Bonus for multiple different keywords in same category
            if score > 1:
                score *= 1.2
            
            category_scores[category] = score
        
        # Return category with highest score, or 'general' if no matches
        if max(category_scores.values()) > 0:
            return max(category_scores, key=category_scores.get)
        else:
            return 'general'
    
    def get_category_confidence(self, text):
        """Get confidence score for category classification"""
        if not text or len(text.strip()) < 3:
            return 0.0
        
        category_scores = {}
        total_score = 0
        
        for category, patterns in self.beauty_categories.items():
            score = 0
            for pattern in patterns:
                matches = len(pattern.findall(text))
                score += matches
            
            category_scores[category] = score
            total_score += score
        
        if total_score == 0:
            return 0.0
        
        max_score = max(category_scores.values())
        return min(max_score / total_score, 1.0)
    
    def _is_gibberish(self, text):
        """Enhanced gibberish detection using multiple methods"""
        if not text or len(text.strip()) < 3:
            return True
        
        text = text.lower().strip()
        gibberish_score = 0
        
        # Method 1: Check consonant/vowel ratio
        vowels = 'aeiou'
        consonants = 'bcdfghjklmnpqrstvwxyz'
        
        vowel_count = sum(1 for char in text if char in vowels)
        consonant_count = sum(1 for char in text if char in consonants)
        total_letters = vowel_count + consonant_count
        
        if total_letters > 0:
            vowel_ratio = vowel_count / total_letters
            consonant_ratio = consonant_count / total_letters
            
            # Too many consonants or vowels
            if consonant_ratio > 0.8 or vowel_ratio > 0.8:
                gibberish_score += 0.3
        
        # Method 2: Check for random character patterns
        random_patterns = [
            r'[bcdfghjklmnpqrstvwxyz]{5,}',  # Too many consonants
            r'[aeiou]{4,}',  # Too many vowels
            r'[a-z]{1,2}[0-9]{3,}',  # Random char-number combos
            r'[0-9]{3,}[a-z]{1,2}',  # Random number-char combos
            r'(.)\1{3,}',  # Repeated characters
        ]
        
        for pattern in random_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                gibberish_score += 0.2
        
        # Method 3: Check word structure
        words = text.split()
        if words:
            # Check for very short or very long words
            avg_word_length = sum(len(word) for word in words) / len(words)
            if avg_word_length < 2 or avg_word_length > 15:
                gibberish_score += 0.2
            
            # Check for words with no vowels (except common abbreviations)
            no_vowel_words = [word for word in words if len(word) > 2 and not any(v in word.lower() for v in 'aeiou')]
            if len(no_vowel_words) > len(words) * 0.5:
                gibberish_score += 0.3
        
        # Method 4: Check for keyboard patterns
        keyboard_rows = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
        for row in keyboard_rows:
            if any(row[i:i+4] in text for i in range(len(row)-3)):
                gibberish_score += 0.3
        
        return gibberish_score >= self.gibberish_threshold
    
    def _detect_low_effort_content(self, text):
        """Detect low-effort content that should be classified as general"""
        if not text:
            return True
        
        text = text.strip().lower()
        
        # Very short comments
        if len(text) < 5:
            return True
        
        # Only emojis
        if re.match(r'^[😀-🿿\s]+$', text):
            return True
        
        # Only punctuation and spaces
        if re.match(r'^[^\w]+$', text):
            return True
        
        # Single word repeated
        words = text.split()
        if len(words) > 1 and len(set(words)) == 1:
            return True
        
        # Common low-effort phrases
        low_effort_phrases = [
            'first', 'second', 'third', 'early', 'late', 'hi', 'hello', 'hey',
            'ok', 'okay', 'yes', 'no', 'maybe', 'lol', 'haha', 'omg', 'wtf'
        ]
        
        if text in low_effort_phrases:
            return True
        
        return False
    
    def detect_spam(self, text):
        """Enhanced spam detection with gibberish detection"""
        if not text or len(text.strip()) < 2:
            return True
        
        # Check for gibberish first
        if self._is_gibberish(text):
            return True
        
        spam_score = 0
        text_lower = text.lower()
        
        # Check each spam pattern
        for pattern_name, pattern in self.spam_patterns.items():
            if pattern.search(text):
                # Weight different patterns differently
                if pattern_name in ['self_promotion', 'url_pattern', 'bot_patterns']:
                    spam_score += 2  # High weight
                elif pattern_name in ['money_spam', 'contact_spam']:
                    spam_score += 1.5  # Medium-high weight
                else:
                    spam_score += 1  # Standard weight
        
        # Additional spam indicators
        if len(text) < 5 and not any(char.isalpha() for char in text):  # Very short non-alphabetic
            spam_score += 1
        
        if len(set(text_lower.split())) < 2 and len(text) > 10:  # Few unique words in long text
            spam_score += 1
        
        # Check for excessive repetition
        words = text_lower.split()
        if len(words) > 3:
            word_counts = Counter(words)
            most_common_count = word_counts.most_common(1)[0][1]
            if most_common_count > len(words) * 0.6:  # Same word appears >60% of the time
                spam_score += 1
        
        # Check character diversity
        unique_chars = len(set(text_lower.replace(' ', '')))
        if len(text) > 10 and unique_chars < 5:  # Low character diversity
            spam_score += 1
        
        return spam_score >= 2  # Threshold for spam classification
    
    def classify_engagement_type(self, text):
        """Enhanced engagement type classification with better general detection"""
        if not text or self._detect_low_effort_content(text):
            return 'general'
        
        engagement_scores = {}
        text_lower = text.lower()
        
        # Score each engagement type
        for eng_type, pattern in self.engagement_patterns.items():
            matches = len(pattern.findall(text))
            # Weight matches by pattern importance
            if eng_type in ['technique_request', 'product_inquiry']:
                engagement_scores[eng_type] = matches * 2  # Higher weight for valuable engagement
            else:
                engagement_scores[eng_type] = matches
        
        # Additional scoring based on text characteristics
        
        # Boost question score if text ends with question mark
        if text.strip().endswith('?'):
            engagement_scores['question'] = engagement_scores.get('question', 0) + 1
        
        # Boost praise if multiple positive words
        positive_words = ['love', 'amazing', 'beautiful', 'perfect', 'great', 'awesome', 'fantastic']
        positive_count = sum(1 for word in positive_words if word in text_lower)
        if positive_count >= 2:
            engagement_scores['praise'] = engagement_scores.get('praise', 0) + 1
        
        # Detect specific product questions
        product_keywords = ['foundation', 'lipstick', 'eyeshadow', 'mascara', 'concealer', 'blush', 'bronzer']
        if any(keyword in text_lower for keyword in product_keywords):
            engagement_scores['product_inquiry'] = engagement_scores.get('product_inquiry', 0) + 1
        
        # Return the engagement type with highest score
        if max(engagement_scores.values(), default=0) > 0:
            return max(engagement_scores, key=engagement_scores.get)
        else:
            # If no specific engagement pattern, check if it's meaningful content
            words = text_lower.split()
            if len(words) >= 3 and len(set(words)) >= 2:  # At least 3 words with some variety
                return 'general'
            else:
                return 'general'
    
    def classify_relevance(self, comment_text, video_title="", video_description=""):
        """Enhanced relevance classification"""
        if self.detect_spam(comment_text):
            return "spam"
        
        # Handle NaN values from pandas
        video_title = str(video_title) if video_title and str(video_title) != 'nan' else ""
        video_description = str(video_description) if video_description and str(video_description) != 'nan' else ""
        
        if not video_title and not video_description:
            return "general"
        
        # Enhanced keyword matching
        comment_words = set(comment_text.lower().split())
        video_content = (video_title + " " + video_description).lower()
        video_words = set(video_content.split())
        
        # Beauty/makeup specific keywords
        beauty_keywords = {
            'makeup', 'beauty', 'cosmetics', 'skincare', 'foundation', 'concealer',
            'lipstick', 'eyeshadow', 'mascara', 'eyeliner', 'blush', 'bronzer',
            'highlighter', 'contour', 'primer', 'setting', 'powder', 'brush',
            'palette', 'shade', 'color', 'look', 'tutorial', 'technique'
        }
        
        # Check for beauty context
        comment_beauty_words = comment_words.intersection(beauty_keywords)
        video_beauty_words = video_words.intersection(beauty_keywords)
        
        # Calculate different types of overlap
        direct_overlap = len(comment_words.intersection(video_words))
        beauty_overlap = len(comment_beauty_words.intersection(video_beauty_words))
        
        # Calculate ratios
        direct_ratio = direct_overlap / len(comment_words) if comment_words else 0
        beauty_ratio = beauty_overlap / len(comment_beauty_words) if comment_beauty_words else 0
        
        # Enhanced classification logic
        if direct_ratio > 0.3 or beauty_ratio > 0.5:  # Strong relevance
            return "genuine"
        elif direct_ratio > 0.15 or beauty_ratio > 0.25 or comment_beauty_words:  # Some relevance
            return "general"
        else:
            return "general"
    
    def analyze_sentiment_vader(self, text):
        """Analyze sentiment using VADER"""
        scores = self.vader_analyzer.polarity_scores(text)
        
        # Classify based on compound score with adjusted thresholds
        if scores['compound'] >= 0.1:  # Slightly higher threshold for positive
            return 'positive', scores['compound']
        elif scores['compound'] <= -0.1:  # Slightly higher threshold for negative
            return 'negative', scores['compound']
        else:
            return 'neutral', scores['compound']
    
    def analyze_sentiment_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.15:  # Adjusted thresholds
            return 'positive', polarity
        elif polarity < -0.15:
            return 'negative', polarity
        else:
            return 'neutral', polarity
    
    def extract_topics(self, comments_list, n_topics=5):
        """Extract main topics from comments using TF-IDF"""
        # Clean and filter comments
        clean_comments = []
        for comment in comments_list:
            if comment and len(comment.strip()) > 10 and not self._is_gibberish(comment):
                clean_comments.append(comment)
        
        if len(clean_comments) < 2:
            return []
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.8  # Ignore very common words
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
        """Analyze a batch of comments with enhanced processing"""
        results = []
        
        # Pre-extract data to avoid repeated lookups
        comments_data = []
        for idx, row in df.iterrows():
            comment_text = row.get('textOriginal_cleaned', '')
            if comment_text and len(comment_text.strip()) > 0:
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
            video_title = data.get('video_title', '')
            video_description = data.get('video_description', '')
            
            # Core analysis with enhanced methods
            analysis = {
                'comment_id': data['idx'],
                'relevance': self.classify_relevance(comment_text, video_title, video_description),
                'engagement_type': self.classify_engagement_type(comment_text),
                'is_spam': self.detect_spam(comment_text),
                'beauty_category': self.classify_beauty_category(comment_text),
                'category_confidence': self.get_category_confidence(comment_text)
            }
            
            # Sentiment analysis
            vader_sentiment, vader_score = self.analyze_sentiment_vader(comment_text)
            
            # Use TextBlob for smaller batches
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
        """Enhanced quality score generation"""
        score = 0
        
        # Relevance scoring (enhanced)
        relevance_scores = {'genuine': 4, 'general': 2, 'spam': -3}
        score += relevance_scores.get(relevance, 0)
        
        # Engagement scoring (enhanced with new types)
        engagement_scores = {
            'technique_request': 4,  # Highest value
            'product_inquiry': 3,    # High value
            'question': 3,           # High value
            'suggestion': 2,         # Medium value
            'compliment_specific': 2, # Medium value
            'personal_story': 2,     # Medium value
            'praise': 1,             # Lower value (generic)
            'thanks': 1,             # Lower value
            'criticism': 1,          # Can be valuable feedback
            'request_collab': 0,     # Neutral
            'general': 0             # Neutral
        }
        score += engagement_scores.get(engagement_type, 0)
        
        # Sentiment bonus (enhanced)
        if sentiment == 'positive':
            score += 1
        elif sentiment == 'neutral':
            score += 0.5  # Neutral can still be valuable
        # Negative sentiment doesn't get penalty as it can be constructive
        
        # Like count bonus (logarithmic scale, enhanced)
        if like_count > 0:
            score += min(np.log10(like_count + 1) * 0.5, 2)  # Cap at 2 points
        
        # Ensure score is between 0 and 5
        return max(min(score, 5), 0)

# Backward compatibility - create an alias
CommentAnalyzer = EnhancedCommentAnalyzer

if __name__ == "__main__":
    # Test the enhanced analyzer
    analyzer = EnhancedCommentAnalyzer()
    
    # Test with sample comments including gibberish
    sample_comments = [
        "Love this makeup tutorial! Can you do one for evening looks?",  # Good engagement
        "AMAZING!!! 😍😍😍😍😍",  # Low effort but positive
        "Check out my channel for more beauty tips!",  # Self promotion spam
        "What foundation are you using? It looks so natural",  # Product inquiry
        "asdfghjkl qwerty zxcvbnm",  # Gibberish
        "aaaaahhhhh omgggg",  # Low quality
        "xj3k9m2 random text here",  # Random spam
        "This technique doesn't work for my skin type, any alternatives?",  # Constructive criticism
        "Could you please do a tutorial on contouring for round faces?",  # Specific request
        "first",  # Low effort
        "💄💋✨🔥💯",  # Only emojis
        "I have the same skin tone and this foundation looks perfect on you! Where can I buy it?"  # High quality
    ]
    
    print("Enhanced Comment Analysis Results:")
    print("=" * 80)
    
    for i, comment in enumerate(sample_comments, 1):
        relevance = analyzer.classify_relevance(comment, "Foundation Tutorial", "Learn how to apply foundation")
        engagement = analyzer.classify_engagement_type(comment)
        sentiment, score = analyzer.analyze_sentiment_vader(comment)
        is_spam = analyzer.detect_spam(comment)
        quality = analyzer.generate_quality_score(relevance, sentiment, engagement)
        
        print(f"{i}. Comment: {comment}")
        print(f"   Relevance: {relevance} | Engagement: {engagement}")
        print(f"   Sentiment: {sentiment} ({score:.2f}) | Spam: {is_spam}")
        print(f"   Quality Score: {quality:.1f}/5")
        print("-" * 80)