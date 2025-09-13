"""
AI Assistant for L'Oréal Comment Analysis
Provides advanced insights and interactive Q&A using Google Gemini
"""
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
from collections import Counter
import json
import os
from typing import Optional, Dict, Any
import sys

# Add config to path
sys.path.append('config')

try:
    import google.generativeai as genai
    from config.ai_config import AIConfig
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Gemini not available. Install with: pip install google-generativeai")

# Load environment variables first
try:
    from dotenv import load_dotenv
    import os
    
    # Try to load .env from current directory and parent directory
    env_loaded = load_dotenv() or load_dotenv('../.env') or load_dotenv('../../.env')
    
    print(f"✅ Environment variables loaded: {env_loaded}")
    print(f"🔍 GEMINI_API_KEY in environment: {'GEMINI_API_KEY' in os.environ}")
    
    # Debug: show first few characters of API key if present
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"🔑 API Key found (first 10 chars): {api_key[:10]}...")
    else:
        print("❌ GEMINI_API_KEY not found in environment")
        
except ImportError:
    print("⚠️ python-dotenv not available, using system environment variables")
    pass

class AIAssistant:
    # Class-level cache for Gemini responses
    _response_cache = {}
    
    def __init__(self, df=None):
        self.df = df
        self.context_data = {}
        self.gemini_model = None
        self.is_gemini_enabled = False
        
        # Initialize Gemini if available
        self._initialize_gemini()
        
        if df is not None:
            self._prepare_context()
    
    def _initialize_gemini(self):
        """Initialize Gemini AI model with enhanced error handling and validation"""
        self.initialization_errors = []
        self.fallback_reason = None
        self.is_gemini_enabled = False
        
        # Check if dependencies are available
        if not GEMINI_AVAILABLE:
            error_msg = "Gemini dependencies not available. Install with: pip install google-generativeai"
            self.initialization_errors.append(error_msg)
            print(f"⚠️ {error_msg}")
            self._setup_fallback_system("missing_dependency")
            return
        
        # Get API key with improved error handling
        try:
            # Store the API key in the AIConfig class for reuse
            AIConfig.GEMINI_API_KEY = AIConfig.get_api_key()
            
            if not AIConfig.GEMINI_API_KEY:
                error_msg = "No Gemini API key found in environment variables, Streamlit secrets, or .env file"
                self.initialization_errors.append(error_msg)
                print(f"❌ {error_msg}")
                print("💡 See docs/GEMINI_SETUP.md for detailed instructions on setting up your API key")
                self._setup_fallback_system("missing_api_key")
                return
                
            # Mask API key for secure logging
            key_length = len(AIConfig.GEMINI_API_KEY)
            masked_key = AIConfig.GEMINI_API_KEY[:4] + "*" * (key_length - 8) + AIConfig.GEMINI_API_KEY[-4:] if key_length > 8 else "*" * key_length
            print(f"🔑 API Key found: {masked_key}")
            
            # Configure Gemini with the API key
            genai.configure(api_key=AIConfig.GEMINI_API_KEY)
            
            # Validate model availability
            available_models = []
            try:
                print("🔍 Checking available models...")
                model_list = genai.list_models()
                available_models = [model.name for model in model_list]
                print(f"✅ Found {len(available_models)} available models")
                
                # Check if our target model is available
                target_model = AIConfig.GEMINI_MODEL
                if target_model not in [model.name for model in model_list]:
                    print(f"⚠️ Target model '{target_model}' not found in available models")
                    print(f"📋 Available models: {', '.join(available_models[:5])}{'...' if len(available_models) > 5 else ''}")
                    
                    # Try to find a suitable alternative model
                    alternative_found = False
                    for model_name in available_models:
                        if 'gemini' in model_name.lower():
                            print(f"🔄 Switching to available model: {model_name}")
                            AIConfig.GEMINI_MODEL = model_name
                            alternative_found = True
                            break
                    
                    if not alternative_found:
                        error_msg = f"No suitable Gemini model found among available models"
                        self.initialization_errors.append(error_msg)
                        print(f"❌ {error_msg}")
                        self._setup_fallback_system("no_suitable_model")
                        return
            except Exception as model_err:
                error_msg = f"Error listing models: {model_err}"
                self.initialization_errors.append(error_msg)
                print(f"⚠️ {error_msg}")
                self._setup_fallback_system("model_listing_error")
                return
            
            # Create the model with validation
            try:
                self.gemini_model = genai.GenerativeModel(AIConfig.GEMINI_MODEL)
                print(f"✅ Gemini model created: {AIConfig.GEMINI_MODEL}")
                
                # Test the model with a simple prompt to verify it's working
                try:
                    print("🧪 Testing model with simple prompt...")
                    test_response = self.gemini_model.generate_content("Respond with 'OK' if you can receive this message.")
                    if test_response and hasattr(test_response, 'text') and 'ok' in test_response.text.lower():
                        print("✅ Model test successful!")
                        self.is_gemini_enabled = True
                        print(f"✅ Gemini AI initialized successfully with model: {AIConfig.GEMINI_MODEL}")
                    else:
                        error_msg = "Model test produced unexpected response"
                        self.initialization_errors.append(error_msg)
                        print(f"⚠️ {error_msg}")
                        self._setup_fallback_system("model_test_failed")
                except Exception as test_err:
                    error_msg = f"Model test failed: {test_err}"
                    self.initialization_errors.append(error_msg)
                    print(f"⚠️ {error_msg}")
                    self._setup_fallback_system("model_test_error")
            except Exception as model_err:
                error_msg = f"Error creating model: {model_err}"
                self.initialization_errors.append(error_msg)
                print(f"❌ {error_msg}")
                self._setup_fallback_system("model_creation_error")
        except Exception as e:
            error_msg = f"Unexpected error during Gemini initialization: {e}"
            self.initialization_errors.append(error_msg)
            print(f"❌ {error_msg}")
            self._setup_fallback_system("unexpected_error")
    
    def _setup_fallback_system(self, error_type):
        """Set up fallback system when Gemini is unavailable"""
        self.is_gemini_enabled = False
        self.fallback_reason = error_type
        
        print("🔄 Setting up rule-based fallback system")
        
        # Provide specific guidance based on error type
        if error_type == "missing_dependency":
            print("💡 To enable Gemini AI, install required package: pip install google-generativeai")
        elif error_type == "missing_api_key":
            print("💡 To enable Gemini AI, set GOOGLE_API_KEY environment variable")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
        elif error_type == "no_suitable_model" or error_type == "model_listing_error":
            print("💡 Check your Google AI Studio account for model access: https://makersuite.google.com/")
        elif error_type == "quota_exceeded":
            print("💡 Your Gemini API quota has been exceeded. Consider upgrading your plan.")
        
        print("✅ Rule-based fallback system ready")
        print("ℹ️ The system will use data-driven rules to answer questions")
        print("ℹ️ For best results, enable Gemini AI by resolving the issues above")
    
    def _prepare_context(self):
        """Prepare context data for AI analysis"""
        if self.df is None or self.df.empty:
            return
        
        # Basic statistics
        self.context_data = {
            'total_comments': len(self.df),
            'spam_rate': (self.df.get('is_spam', pd.Series()) == True).mean() * 100,
            'avg_quality': self.df.get('quality_score', pd.Series()).mean(),
            'sentiment_dist': self.df.get('vader_sentiment', pd.Series()).value_counts(normalize=True).to_dict(),
            'relevance_dist': self.df.get('relevance', pd.Series()).value_counts(normalize=True).to_dict(),
            'engagement_dist': self.df.get('engagement_type', pd.Series()).value_counts(normalize=True).to_dict(),
        }
        
        # Advanced metrics
        if 'likeCount' in self.df.columns:
            self.context_data['avg_likes'] = self.df['likeCount'].mean()
            self.context_data['total_likes'] = self.df['likeCount'].sum()
        
        if 'textOriginal_cleaned' in self.df.columns:
            self.context_data['avg_comment_length'] = self.df['textOriginal_cleaned'].str.len().mean()
    
    def generate_advanced_insights(self):
        """Generate advanced AI-powered insights"""
        insights = []
        
        if self.df is None or self.df.empty:
            return ["No data available for analysis"]
        
        # Engagement Quality Analysis
        insights.extend(self._analyze_engagement_quality())
        
        # Content Performance Insights
        insights.extend(self._analyze_content_performance())
        
        # Audience Behavior Patterns
        insights.extend(self._analyze_audience_behavior())
        
        # Competitive Intelligence
        insights.extend(self._generate_competitive_insights())
        
        # Actionable Recommendations
        insights.extend(self._generate_recommendations())
        
        return insights
    
    def _analyze_engagement_quality(self):
        """Analyze engagement quality patterns"""
        insights = []
        
        if 'engagement_type' not in self.df.columns:
            return insights
        
        engagement_counts = self.df['engagement_type'].value_counts()
        total_comments = len(self.df)
        
        # Question engagement analysis
        question_rate = engagement_counts.get('question', 0) / total_comments * 100
        if question_rate > 25:
            insights.append(f"🤔 High Question Rate ({question_rate:.1f}%): Your audience is highly curious and engaged. Consider creating FAQ content or Q&A videos to address common questions.")
        elif question_rate > 15:
            insights.append(f"❓ Moderate Question Rate ({question_rate:.1f}%): Good audience engagement. Consider occasional Q&A sessions to boost interaction.")
        
        # Technique request analysis
        technique_rate = engagement_counts.get('technique_request', 0) / total_comments * 100
        if technique_rate > 20:
            insights.append(f"🎯 High Technique Demand ({technique_rate:.1f}%): Strong demand for educational content. Focus on step-by-step tutorials and technique breakdowns.")
        
        # Praise vs criticism ratio
        praise_rate = engagement_counts.get('praise', 0) / total_comments * 100
        if praise_rate > 40:
            insights.append(f"💖 High Praise Rate ({praise_rate:.1f}%): Excellent content reception. Your audience loves your content - consider similar content themes.")
        
        return insights
    
    def _analyze_content_performance(self):
        """Analyze content performance patterns"""
        insights = []
        
        if 'quality_score' not in self.df.columns:
            return insights
        
        avg_quality = self.df['quality_score'].mean()
        high_quality_rate = (self.df['quality_score'] >= 4).mean() * 100
        
        if avg_quality >= 3.5:
            insights.append(f"⭐ Excellent Content Quality (Score: {avg_quality:.2f}/5): Your content generates high-quality engagement. {high_quality_rate:.1f}% of comments are high-quality.")
        elif avg_quality >= 2.5:
            insights.append(f"📈 Good Content Quality (Score: {avg_quality:.2f}/5): Solid engagement with room for improvement. Focus on increasing meaningful interactions.")
        else:
            insights.append(f"🔧 Content Quality Opportunity (Score: {avg_quality:.2f}/5): Consider strategies to encourage more meaningful engagement from your audience.")
        
        # Analyze quality by video if title is available
        if 'title' in self.df.columns:
            video_quality = self.df.groupby('title')['quality_score'].mean().sort_values(ascending=False)
            if len(video_quality) > 1:
                best_video = video_quality.index[0]
                best_score = video_quality.iloc[0]
                insights.append(f"🏆 Top Performing Content: '{best_video[:50]}...' (Quality Score: {best_score:.2f}) - Analyze this content style for future videos.")
        
        return insights
    
    def _analyze_audience_behavior(self):
        """Analyze audience behavior patterns"""
        insights = []
        
        if 'textOriginal_cleaned' not in self.df.columns:
            return insights
        
        # Comment length analysis
        avg_length = self.df['textOriginal_cleaned'].str.len().mean()
        long_comments = (self.df['textOriginal_cleaned'].str.len() > 100).mean() * 100
        
        if avg_length > 80:
            insights.append(f"📝 Highly Engaged Audience: Average comment length is {avg_length:.0f} characters. {long_comments:.1f}% are detailed comments - your audience is deeply invested.")
        elif avg_length < 30:
            insights.append(f"⚡ Quick Engagement Style: Short average comments ({avg_length:.0f} chars). Consider content that encourages more detailed feedback.")
        
        # Emoji usage analysis
        emoji_pattern = re.compile(r'[😀-🿿]')
        emoji_comments = self.df['textOriginal_cleaned'].apply(lambda x: bool(emoji_pattern.search(str(x)))).mean() * 100
        
        if emoji_comments > 60:
            insights.append(f"😊 Expressive Audience: {emoji_comments:.1f}% of comments contain emojis. Your audience is emotionally engaged and expressive.")
        
        return insights
    
    def _generate_competitive_insights(self):
        """Generate competitive intelligence insights"""
        insights = []
        
        if 'relevance' not in self.df.columns:
            return insights
        
        genuine_rate = (self.df['relevance'] == 'genuine').mean() * 100
        spam_rate = (self.df['relevance'] == 'spam').mean() * 100
        
        if genuine_rate > 70:
            insights.append(f"🎯 Strong Brand Loyalty: {genuine_rate:.1f}% genuine engagement indicates strong audience connection and brand loyalty.")
        elif genuine_rate < 40:
            insights.append(f"🔍 Engagement Opportunity: {genuine_rate:.1f}% genuine engagement. Focus on building stronger community connections.")
        
        if spam_rate < 5:
            insights.append(f"🛡️ Clean Community: Low spam rate ({spam_rate:.1f}%) indicates good community management and authentic audience.")
        elif spam_rate > 20:
            insights.append(f"⚠️ Community Management Alert: High spam rate ({spam_rate:.1f}%). Consider stricter moderation or community guidelines.")
        
        return insights
    
    def _generate_recommendations(self):
        """Generate actionable AI recommendations"""
        recommendations = []
        
        if self.df is None or self.df.empty:
            return recommendations
        
        # Content strategy recommendations
        if 'engagement_type' in self.df.columns:
            engagement_dist = self.df['engagement_type'].value_counts(normalize=True)
            
            if engagement_dist.get('question', 0) > 0.2:
                recommendations.append("💡 Content Strategy: Create a weekly Q&A series to address audience questions and boost engagement.")
            
            if engagement_dist.get('technique_request', 0) > 0.15:
                recommendations.append("🎓 Educational Content: Develop detailed tutorial series focusing on techniques your audience requests most.")
            
            if engagement_dist.get('praise', 0) > 0.3:
                recommendations.append("🌟 Community Building: Leverage positive sentiment by featuring user testimonials and creating user-generated content campaigns.")
        
        # Performance optimization
        if 'quality_score' in self.df.columns:
            low_quality_rate = (self.df['quality_score'] < 2).mean()
            if low_quality_rate > 0.3:
                recommendations.append("📊 Engagement Optimization: 30%+ low-quality comments detected. Consider call-to-action improvements and community engagement strategies.")
        
        # Timing and frequency
        if 'publishedAt' in self.df.columns:
            try:
                self.df['hour'] = pd.to_datetime(self.df['publishedAt']).dt.hour
                peak_hours = self.df['hour'].value_counts().head(3).index.tolist()
                recommendations.append(f"⏰ Optimal Timing: Peak engagement hours are {peak_hours}. Consider posting during these times for maximum reach.")
            except:
                pass
        
        return recommendations
    
    def answer_question(self, question):
        """AI assistant to answer questions about the analysis using Gemini"""
        if self.df is None or self.df.empty:
            return "I don't have any data to analyze yet. Please upload and analyze your CSV files first!"
        
        # Use Gemini if available, otherwise fallback to rule-based
        if self.is_gemini_enabled:
            return self._answer_with_gemini(question)
        else:
            return self._answer_with_rules(question)
    
    def get_short_answer(self, question):
        """Get a short, concise answer (max 2-3 sentences)"""
        if self.df is None or self.df.empty:
            return "No data available for analysis."
        
        question_lower = question.lower()
        
        # Quick responses for common questions
        if any(word in question_lower for word in ['spam', 'fake']):
            spam_rate = (self.df.get('is_spam', pd.Series()) == True).mean() * 100
            if spam_rate < 10:
                return f"✅ Low spam rate: {spam_rate:.1f}%. Your community is healthy!"
            elif spam_rate < 20:
                return f"⚠️ Moderate spam: {spam_rate:.1f}%. Consider enhanced moderation."
            else:
                return f"🚨 High spam: {spam_rate:.1f}%. Implement stricter controls immediately."
        
        elif any(word in question_lower for word in ['sentiment', 'positive', 'negative']):
            positive_rate = (self.df.get('vader_sentiment', pd.Series()) == 'positive').mean() * 100
            if positive_rate > 70:
                return f"😊 Excellent sentiment: {positive_rate:.1f}% positive. Audience loves your content!"
            elif positive_rate > 50:
                return f"👍 Good sentiment: {positive_rate:.1f}% positive. Room for improvement."
            else:
                return f"😐 Mixed sentiment: {positive_rate:.1f}% positive. Focus on audience engagement."
        
        elif any(word in question_lower for word in ['quality', 'score']):
            avg_quality = self.df.get('quality_score', pd.Series()).mean()
            if avg_quality > 3.5:
                return f"⭐ High quality: {avg_quality:.1f}/5. Excellent engagement!"
            elif avg_quality > 2.5:
                return f"👍 Good quality: {avg_quality:.1f}/5. Some improvement possible."
            else:
                return f"📈 Quality needs work: {avg_quality:.1f}/5. Focus on better content."
        
        elif any(word in question_lower for word in ['engagement', 'interact']):
            engagement_dist = self.df.get('engagement_type', pd.Series()).value_counts(normalize=True)
            top_engagement = engagement_dist.index[0] if len(engagement_dist) > 0 else 'general'
            percentage = engagement_dist.iloc[0] * 100 if len(engagement_dist) > 0 else 0
            return f"🎯 Top engagement: {top_engagement} ({percentage:.1f}%). Focus on this type!"
        
        elif any(word in question_lower for word in ['recommend', 'tip', 'advice']):
            spam_rate = (self.df.get('is_spam', pd.Series()) == True).mean() * 100
            avg_quality = self.df.get('quality_score', pd.Series()).mean()
            
            if spam_rate > 15:
                return "🛡️ Priority: Reduce spam with better moderation and community guidelines."
            elif avg_quality < 3.0:
                return "⭐ Priority: Improve content quality with engaging call-to-actions."
            else:
                return "🎯 Priority: Maintain current quality and expand successful content themes."
        
        else:
            # General summary
            total = len(self.df)
            spam_rate = (self.df.get('is_spam', pd.Series()) == True).mean() * 100
            avg_quality = self.df.get('quality_score', pd.Series()).mean()
            return f"📊 Summary: {total:,} comments, {spam_rate:.1f}% spam, {avg_quality:.1f}/5 quality."
    
    def _answer_with_gemini(self, question):
        """Answer questions using Gemini AI with enhanced prompt engineering, caching, and robust fallback"""
        # Check if Gemini is enabled before attempting to use it
        if not self.is_gemini_enabled:
            print(f"⚠️ Gemini not available (reason: {self.fallback_reason}), using rule-based fallback system")
            return self._answer_with_rules(question)
        
        # Generate a cache key based on the question and data context hash
        import hashlib
        data_hash = hashlib.md5(str(self.df.shape).encode()).hexdigest()[:8] if self.df is not None else "nodata"
        cache_key = f"{question}_{data_hash}"
        
        # Check if response is in cache
        if cache_key in AIAssistant._response_cache:
            print(f"🔄 Using cached response for question: {question[:30]}...")
            return AIAssistant._response_cache[cache_key]
        
        try:
            # Prepare data context for Gemini
            data_context = self._prepare_gemini_context()
            
            # Determine question type for specialized prompts
            question_lower = question.lower()
            question_type = "general"
            
            if any(word in question_lower for word in ['spam', 'fake', 'bot']):
                question_type = "spam"
            elif any(word in question_lower for word in ['sentiment', 'positive', 'negative', 'feel', 'emotion']):
                question_type = "sentiment"
            elif any(word in question_lower for word in ['engagement', 'interact', 'comment', 'participation']):
                question_type = "engagement"
            elif any(word in question_lower for word in ['content', 'strategy', 'plan', 'recommend', 'future']):
                question_type = "content_strategy"
            
            # Get specialized prompt if available
            specialized_prompt = AIConfig.get_specialized_prompt(question_type)
            
            # Create the enhanced prompt with specialized instructions
            prompt = f"""
            {AIConfig.SYSTEM_PROMPT}
            
            {specialized_prompt}
            
            DATA CONTEXT:
            {data_context}
            
            USER QUESTION: {question}
            
            IMPORTANT INSTRUCTIONS:
            1. Analyze the data thoroughly before responding
            2. Include specific metrics and percentages from the data
            3. Structure your response with clear sections
            4. Provide at least 3 specific, actionable recommendations
            5. Use formatting (bold, bullets, etc.) to highlight key points
            6. Begin with a brief summary of your findings
            7. End with concrete next steps
            """
            
            print(f"🔍 Sending request to Gemini model: {AIConfig.GEMINI_MODEL}")
            print(f"📝 Using specialized prompt for: {question_type}")
            
            # Set timeout for API call to prevent hanging
            import time
            start_time = time.time()
            
            # Generate response with enhanced configuration
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=AIConfig.MAX_TOKENS,
                    temperature=AIConfig.TEMPERATURE,
                    top_p=0.95,  # Add top_p for better quality
                    top_k=40,    # Add top_k for better quality
                )
            )
            
            elapsed_time = time.time() - start_time
            print(f"✅ Received response from Gemini in {elapsed_time:.2f} seconds")
            
            # Process the response to ensure it's well-formatted
            response_text = response.text
            
            # Add a signature to indicate Gemini was used
            response_text += "\n\n_Analysis powered by Google Gemini_"
            
            # Store in cache before returning
            AIAssistant._response_cache[cache_key] = response_text
            print(f"💾 Response cached (cache size: {len(AIAssistant._response_cache)})")
            
            # Limit cache size to prevent memory issues (keep most recent 50 responses)
            if len(AIAssistant._response_cache) > 50:
                # Remove oldest cache entry
                oldest_key = next(iter(AIAssistant._response_cache))
                AIAssistant._response_cache.pop(oldest_key)
                print(f"🧹 Removed oldest cache entry to maintain cache size")
            
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini error: {e}")
            
            # Check if it's a quota error
            if "quota" in error_msg.lower() or "429" in error_msg:
                print("⚠️ API quota exceeded, switching to fallback system")
                self._setup_fallback_system("quota_exceeded")
                fallback_response = self._answer_with_rules(question)
                formatted_response = f"🤖 **AI Assistant** (Data-driven analysis):\n\n{fallback_response}\n\n" + \
                       f"💡 *Note: Using enhanced data analysis due to API limits. Upgrade your Gemini plan for full AI responses.*"
                
                # Cache the fallback response too
                AIAssistant._response_cache[cache_key] = formatted_response
                print(f"💾 Fallback response cached for quota error")
                
                return formatted_response
            else:
                # Other errors - use fallback
                print(f"🔄 Gemini error, falling back to rule-based system: {error_msg}")
                fallback_response = self._answer_with_rules(question)
                
                # Cache the fallback response
                AIAssistant._response_cache[cache_key] = fallback_response
                print(f"💾 Fallback response cached for general error")
                
                return fallback_response
    
    def _prepare_gemini_context(self):
        """Prepare comprehensive data context for Gemini with advanced insights"""
        if self.df is None or self.df.empty:
            return "No data available"
        
        # Basic statistics
        total_comments = len(self.df)
        
        # Spam analysis
        spam_rate = (self.df.get('is_spam', pd.Series()) == True).mean() * 100
        
        # Quality analysis
        quality_scores = self.df.get('quality_score', pd.Series())
        avg_quality = quality_scores.mean()
        high_quality_rate = (quality_scores >= 4).mean() * 100
        low_quality_rate = (quality_scores < 2).mean() * 100
        
        # Sentiment analysis
        sentiment_dist = self.df.get('vader_sentiment', pd.Series()).value_counts(normalize=True) * 100
        
        # Engagement analysis
        engagement_dist = self.df.get('engagement_type', pd.Series()).value_counts(normalize=True) * 100
        
        # Relevance analysis
        relevance_dist = self.df.get('relevance', pd.Series()).value_counts(normalize=True) * 100
        
        # Trend analysis (if timestamp available)
        trend_analysis = self._format_trend_analysis()
        
        # Sentiment ratio and change over time
        sentiment_ratio = self._format_sentiment_ratio(sentiment_dist)
        
        # Engagement quality breakdown
        engagement_quality = self._format_engagement_quality(engagement_dist)
        
        # Comment length analysis
        comment_length_analysis = self._format_comment_length_analysis()
        
        # Video performance comparison (if available)
        video_performance = self._format_video_metrics()
        
        # Content themes and topics
        content_themes = self._format_content_themes()
        
        # Sample comments by category
        sample_comments = self._format_sample_comments()
        
        context = f"""
COMMENT ANALYSIS DATA SUMMARY:

BASIC METRICS:
- Total Comments Analyzed: {total_comments:,}
- Average Quality Score: {avg_quality:.2f}/5
- High Quality Comments (4-5): {high_quality_rate:.1f}%
- Low Quality Comments (0-2): {low_quality_rate:.1f}%

SPAM & AUTHENTICITY:
- Spam Rate: {spam_rate:.1f}%
- Genuine Comments: {relevance_dist.get('genuine', 0):.1f}%
- Promotional Content: {relevance_dist.get('promotional', 0):.1f}%

SENTIMENT BREAKDOWN:
- Positive Sentiment: {sentiment_dist.get('positive', 0):.1f}%
- Neutral Sentiment: {sentiment_dist.get('neutral', 0):.1f}%
- Negative Sentiment: {sentiment_dist.get('negative', 0):.1f}%
{sentiment_ratio}

ENGAGEMENT TYPES:
- Praise/Compliments: {engagement_dist.get('praise', 0):.1f}%
- Questions: {engagement_dist.get('question', 0):.1f}%
- Technique Requests: {engagement_dist.get('technique_request', 0):.1f}%
- General Comments: {engagement_dist.get('general', 0):.1f}%
- Product Inquiries: {engagement_dist.get('product_inquiry', 0):.1f}%
{engagement_quality}

{comment_length_analysis}

{trend_analysis}

{video_performance}

{content_themes}

{sample_comments}
"""
        
        return context
    
    def _answer_with_rules(self, question):
        """Data-driven fallback answering system"""
        question_lower = question.lower()
        
        # Get actual data insights
        insights = self._get_data_insights()
        
        # Question routing based on keywords - but use actual data
        if any(word in question_lower for word in ['spam', 'fake', 'bot']):
            return self._generate_spam_insight(insights)
        
        elif any(word in question_lower for word in ['sentiment', 'positive', 'negative', 'emotion']):
            return self._generate_sentiment_insight(insights)
        
        elif any(word in question_lower for word in ['engagement', 'interact', 'participate']):
            return self._generate_engagement_insight(insights)
        
        elif any(word in question_lower for word in ['quality', 'score', 'rating']):
            return self._generate_quality_insight(insights)
        
        elif any(word in question_lower for word in ['recommend', 'suggest', 'improve', 'strategy']):
            return self._generate_recommendations_insight(insights)
        
        elif any(word in question_lower for word in ['trend', 'pattern', 'insight']):
            return self._generate_trend_insight(insights)
        
        elif any(word in question_lower for word in ['video', 'content', 'performance']):
            return self._generate_content_insight(insights)
        
        else:
            return self._generate_general_insight(insights)
    
    def _get_data_insights(self):
        """Get comprehensive data insights for responses"""
        if self.df is None or self.df.empty:
            return {"error": "No data available"}
        
        insights = {}
        
        # Basic metrics
        insights['total_comments'] = len(self.df)
        
        # Spam analysis
        if 'is_spam' in self.df.columns:
            insights['spam_rate'] = (self.df['is_spam'] == True).mean() * 100
            insights['spam_count'] = (self.df['is_spam'] == True).sum()
        
        # Quality analysis
        if 'quality_score' in self.df.columns:
            insights['avg_quality'] = self.df['quality_score'].mean()
            insights['high_quality_rate'] = (self.df['quality_score'] >= 4).mean() * 100
            insights['low_quality_rate'] = (self.df['quality_score'] < 2).mean() * 100
        
        # Sentiment analysis
        if 'vader_sentiment' in self.df.columns:
            sentiment_counts = self.df['vader_sentiment'].value_counts(normalize=True) * 100
            insights['sentiment'] = sentiment_counts.to_dict()
            insights['positive_rate'] = sentiment_counts.get('positive', 0)
            insights['negative_rate'] = sentiment_counts.get('negative', 0)
        
        # Engagement analysis
        if 'engagement_type' in self.df.columns:
            engagement_counts = self.df['engagement_type'].value_counts(normalize=True) * 100
            insights['engagement'] = engagement_counts.to_dict()
            insights['top_engagement'] = engagement_counts.index[0] if len(engagement_counts) > 0 else 'general'
        
        # Relevance analysis
        if 'relevance' in self.df.columns:
            relevance_counts = self.df['relevance'].value_counts(normalize=True) * 100
            insights['relevance'] = relevance_counts.to_dict()
            insights['genuine_rate'] = relevance_counts.get('genuine', 0)
        
        return insights
    
    def _generate_spam_insight(self, insights):
        """Generate spam-related insights from actual data"""
        if 'spam_rate' not in insights:
            return "Spam analysis not available in your dataset."
        
        spam_rate = insights['spam_rate']
        spam_count = insights.get('spam_count', 0)
        total = insights['total_comments']
        
        response = f"📊 **Spam Analysis Results:**\n\n"
        response += f"• **Spam Rate:** {spam_rate:.1f}% ({spam_count:,} out of {total:,} comments)\n"
        
        if spam_rate < 5:
            response += f"• **Status:** ✅ Excellent - Very low spam rate\n"
            response += f"• **Insight:** Your community is healthy with minimal spam activity\n"
            response += f"• **Action:** Continue current moderation practices\n"
        elif spam_rate < 15:
            response += f"• **Status:** 🟡 Good - Acceptable spam levels\n"
            response += f"• **Insight:** Moderate spam activity detected\n"
            response += f"• **Action:** Monitor trends and consider enhanced filtering\n"
        else:
            response += f"• **Status:** 🔴 Needs Attention - High spam rate\n"
            response += f"• **Insight:** Significant spam activity affecting your community\n"
            response += f"• **Action:** Implement stricter moderation and community guidelines\n"
        
        return response
    
    def _generate_sentiment_insight(self, insights):
        """Generate sentiment insights from actual data"""
        if 'sentiment' not in insights:
            return "Sentiment analysis not available in your dataset."
        
        sentiment = insights['sentiment']
        positive_rate = insights.get('positive_rate', 0)
        negative_rate = insights.get('negative_rate', 0)
        
        response = f"😊 **Audience Sentiment Analysis:**\n\n"
        
        for mood, percentage in sentiment.items():
            emoji = "😊" if mood == "positive" else "😐" if mood == "neutral" else "😞"
            response += f"• **{mood.title()}:** {emoji} {percentage:.1f}%\n"
        
        response += f"\n**Overall Assessment:**\n"
        if positive_rate > 60:
            response += f"✅ Excellent positive sentiment! Your audience loves your content.\n"
        elif positive_rate > 40:
            response += f"🟡 Good sentiment balance with room for improvement.\n"
        else:
            response += f"🔴 Consider strategies to increase positive engagement.\n"
        
        return response
    
    def _generate_engagement_insight(self, insights):
        """Generate engagement insights from actual data"""
        if 'engagement' not in insights:
            return "Engagement analysis not available in your dataset."
        
        engagement = insights['engagement']
        top_engagement = insights.get('top_engagement', 'general')
        
        response = f"🎯 **Engagement Pattern Analysis:**\n\n"
        
        for eng_type, percentage in engagement.items():
            response += f"• **{eng_type.replace('_', ' ').title()}:** {percentage:.1f}%\n"
        
        response += f"\n**Key Insight:**\n"
        response += f"Your audience primarily engages through **{top_engagement.replace('_', ' ')}** "
        response += f"({engagement.get(top_engagement, 0):.1f}% of interactions).\n"
        
        if top_engagement == 'question':
            response += f"\n💡 **Recommendation:** Your audience is curious! Consider Q&A content or FAQ videos."
        elif top_engagement == 'praise':
            response += f"\n💡 **Recommendation:** Great audience satisfaction! Maintain your current content quality."
        elif top_engagement == 'technique_request':
            response += f"\n💡 **Recommendation:** High demand for tutorials! Focus on educational content."
        
        return response
    
    def _generate_quality_insight(self, insights):
        """Generate quality insights from actual data"""
        if 'avg_quality' not in insights:
            return "Quality analysis not available in your dataset."
        
        avg_quality = insights['avg_quality']
        high_quality_rate = insights.get('high_quality_rate', 0)
        low_quality_rate = insights.get('low_quality_rate', 0)
        
        response = f"⭐ **Comment Quality Analysis:**\n\n"
        response += f"• **Average Quality Score:** {avg_quality:.2f}/5\n"
        response += f"• **High Quality Comments (4-5):** {high_quality_rate:.1f}%\n"
        response += f"• **Low Quality Comments (0-2):** {low_quality_rate:.1f}%\n"
        
        response += f"\n**Assessment:**\n"
        if avg_quality >= 4:
            response += f"🌟 Outstanding! Your content generates high-quality engagement.\n"
        elif avg_quality >= 3:
            response += f"👍 Good quality with room for improvement.\n"
        else:
            response += f"📈 Focus on strategies to encourage more meaningful interactions.\n"
        
        return response
        
    def _format_trend_analysis(self):
        """Format trend analysis data for Gemini context"""
        if self.df is None or self.df.empty or 'publishedAt' not in self.df.columns:
            return ""
        
        try:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(self.df['publishedAt']):
                self.df['publishedAt'] = pd.to_datetime(self.df['publishedAt'], errors='coerce')
            
            # Group by week and calculate metrics
            self.df['week'] = self.df['publishedAt'].dt.isocalendar().week
            weekly_data = self.df.groupby('week').agg({
                'quality_score': 'mean',
                'vader_score': 'mean',
                'textOriginal_cleaned': 'count'
            }).reset_index()
            
            # Calculate week-over-week changes
            weekly_data['quality_change'] = weekly_data['quality_score'].diff()
            weekly_data['sentiment_change'] = weekly_data['vader_score'].diff()
            weekly_data['volume_change'] = weekly_data['textOriginal_cleaned'].diff()
            
            # Get latest week's changes
            latest = weekly_data.iloc[-1]
            
            # Format trend insights
            trend_text = "TREND ANALYSIS (WEEK-OVER-WEEK):\n"
            
            # Quality trend
            if latest['quality_change'] > 0.2:
                trend_text += "- Quality Score: ↗️ Significant improvement\n"
            elif latest['quality_change'] > 0:
                trend_text += "- Quality Score: ↗️ Slight improvement\n"
            elif latest['quality_change'] < -0.2:
                trend_text += "- Quality Score: ↘️ Significant decline\n"
            elif latest['quality_change'] < 0:
                trend_text += "- Quality Score: ↘️ Slight decline\n"
            else:
                trend_text += "- Quality Score: → Stable\n"
            
            # Sentiment trend
            if latest['sentiment_change'] > 0.1:
                trend_text += "- Sentiment: ↗️ Becoming more positive\n"
            elif latest['sentiment_change'] < -0.1:
                trend_text += "- Sentiment: ↘️ Becoming more negative\n"
            else:
                trend_text += "- Sentiment: → Stable sentiment\n"
            
            # Volume trend
            if latest['volume_change'] > 10:
                trend_text += "- Comment Volume: ↗️ Increasing engagement\n"
            elif latest['volume_change'] < -10:
                trend_text += "- Comment Volume: ↘️ Decreasing engagement\n"
            else:
                trend_text += "- Comment Volume: → Stable engagement volume\n"
                
            return trend_text
        except Exception as e:
            print(f"Error in trend analysis: {e}")
            return ""
    
    def _format_sentiment_ratio(self, sentiment_dist):
        """Format sentiment ratio analysis for Gemini context"""
        if sentiment_dist is None or len(sentiment_dist) == 0:
            return ""
        
        try:
            # Calculate positive to negative ratio
            positive = sentiment_dist.get('positive', 0)
            negative = sentiment_dist.get('negative', 0)
            
            if negative > 0:
                ratio = positive / negative
                ratio_text = f"- Positive-to-Negative Ratio: {ratio:.1f}:1\n"
                
                if ratio >= 5:
                    ratio_text += "  (Excellent sentiment balance - overwhelmingly positive)\n"
                elif ratio >= 3:
                    ratio_text += "  (Very good sentiment balance - strongly positive)\n"
                elif ratio >= 2:
                    ratio_text += "  (Good sentiment balance - moderately positive)\n"
                elif ratio >= 1:
                    ratio_text += "  (Fair sentiment balance - slightly positive)\n"
                else:
                    ratio_text += "  (Concerning sentiment balance - more negative than positive)\n"
            else:
                ratio_text = "- Positive-to-Negative Ratio: ∞:1 (No negative comments)\n"
                
            return ratio_text
        except Exception as e:
            print(f"Error in sentiment ratio analysis: {e}")
            return ""
    
    def _format_engagement_quality(self, engagement_dist):
        """Format engagement quality analysis for Gemini context"""
        if engagement_dist is None or len(engagement_dist) == 0:
            return ""
        
        try:
            # Calculate meaningful engagement percentage
            meaningful_types = ['question', 'technique_request', 'suggestion', 'product_inquiry']
            meaningful_engagement = sum(engagement_dist.get(t, 0) for t in meaningful_types)
            
            quality_text = f"- Meaningful Engagement: {meaningful_engagement:.1f}%\n"
            
            # Add interpretation
            if meaningful_engagement >= 50:
                quality_text += "  (Excellent - Your content drives substantive interaction)\n"
            elif meaningful_engagement >= 30:
                quality_text += "  (Good - Your content encourages thoughtful engagement)\n"
            elif meaningful_engagement >= 15:
                quality_text += "  (Fair - Some meaningful interaction, room for improvement)\n"
            else:
                quality_text += "  (Low - Consider strategies to encourage more meaningful engagement)\n"
                
            return quality_text
        except Exception as e:
            print(f"Error in engagement quality analysis: {e}")
            return ""
    
    def _format_comment_length_analysis(self):
        """Format comment length analysis for Gemini context"""
        if self.df is None or self.df.empty or 'textOriginal_cleaned' not in self.df.columns:
            return ""
        
        try:
            # Calculate comment length metrics
            self.df['comment_length'] = self.df['textOriginal_cleaned'].str.len()
            
            avg_length = self.df['comment_length'].mean()
            short_comments = (self.df['comment_length'] < 50).mean() * 100
            long_comments = (self.df['comment_length'] > 150).mean() * 100
            
            length_text = "COMMENT LENGTH ANALYSIS:\n"
            length_text += f"- Average Comment Length: {avg_length:.1f} characters\n"
            length_text += f"- Short Comments (<50 chars): {short_comments:.1f}%\n"
            length_text += f"- Long Comments (>150 chars): {long_comments:.1f}%\n"
            
            # Add interpretation
            if long_comments > 30:
                length_text += "  (Excellent - Your audience is highly engaged and detailed)\n"
            elif long_comments > 15:
                length_text += "  (Good - Your content inspires thoughtful responses)\n"
            elif short_comments > 70:
                length_text += "  (Concerning - Many brief, potentially low-effort comments)\n"
            else:
                length_text += "  (Average - Typical comment length distribution)\n"
                
            return length_text
        except Exception as e:
            print(f"Error in comment length analysis: {e}")
            return ""
    
    def _format_video_metrics(self):
        """Format video performance metrics for Gemini context"""
        if self.df is None or self.df.empty or 'title' not in self.df.columns:
            return ""
        
        try:
            # Calculate video performance metrics
            video_stats = self.df.groupby('title').agg({
                'quality_score': 'mean',
                'textOriginal_cleaned': 'count',
                'vader_score': 'mean'
            }).round(2)
            
            video_stats.columns = ['Avg_Quality', 'Comment_Count', 'Sentiment_Score']
            
            # Sort by different metrics
            top_by_quality = video_stats.sort_values('Avg_Quality', ascending=False).head(3)
            top_by_engagement = video_stats.sort_values('Comment_Count', ascending=False).head(3)
            top_by_sentiment = video_stats.sort_values('Sentiment_Score', ascending=False).head(3)
            
            # Format the output
            video_text = "VIDEO PERFORMANCE COMPARISON:\n"
            
            video_text += "Top 3 by Quality Score:\n"
            video_text += f"{top_by_quality[['Avg_Quality']].to_string()}\n\n"
            
            video_text += "Top 3 by Comment Volume:\n"
            video_text += f"{top_by_engagement[['Comment_Count']].to_string()}\n\n"
            
            video_text += "Top 3 by Positive Sentiment:\n"
            video_text += f"{top_by_sentiment[['Sentiment_Score']].to_string()}\n"
            
            return video_text
        except Exception as e:
            print(f"Error in video metrics analysis: {e}")
            return ""
    
    def _format_content_themes(self):
        """Format content themes and topics for Gemini context"""
        if self.df is None or self.df.empty or 'textOriginal_cleaned' not in self.df.columns:
            return ""
        
        try:
            # Extract comments for analysis
            comments = self.df['textOriginal_cleaned'].dropna().tolist()
            
            # Simple keyword-based theme extraction
            keywords = {
                'makeup': ['makeup', 'foundation', 'concealer', 'lipstick', 'eyeshadow', 'mascara'],
                'skincare': ['skincare', 'moisturizer', 'cleanser', 'serum', 'sunscreen', 'acne'],
                'haircare': ['hair', 'shampoo', 'conditioner', 'hairstyle', 'haircut', 'color'],
                'tutorial': ['tutorial', 'how to', 'technique', 'steps', 'guide', 'learn'],
                'product': ['product', 'brand', 'purchase', 'buy', 'recommend', 'review']
            }
            
            # Count occurrences
            theme_counts = {theme: 0 for theme in keywords}
            for comment in comments:
                comment = comment.lower()
                for theme, terms in keywords.items():
                    if any(term in comment for term in terms):
                        theme_counts[theme] += 1
            
            # Calculate percentages
            total = len(comments)
            if total > 0:
                theme_percentages = {theme: (count / total) * 100 for theme, count in theme_counts.items()}
                
                # Format the output
                themes_text = "CONTENT THEMES & TOPICS:\n"
                for theme, percentage in sorted(theme_percentages.items(), key=lambda x: x[1], reverse=True):
                    themes_text += f"- {theme.title()}: {percentage:.1f}%\n"
                
                # Add top keywords if available
                try:
                    from collections import Counter
                    import re
                    
                    # Extract words and count frequencies
                    words = []
                    for comment in comments:
                        words.extend(re.findall(r'\b[a-zA-Z]{3,}\b', comment.lower()))
                    
                    # Remove common stopwords
                    stopwords = ['the', 'and', 'this', 'that', 'for', 'you', 'your', 'with', 'have', 'are', 'not']
                    filtered_words = [word for word in words if word not in stopwords]
                    
                    # Get top keywords
                    word_counts = Counter(filtered_words).most_common(5)
                    
                    if word_counts:
                        themes_text += "\nTop Keywords:\n"
                        for word, count in word_counts:
                            themes_text += f"- {word}: {count} mentions\n"
                except Exception as e:
                    print(f"Error extracting keywords: {e}")
                
                return themes_text
            return ""
        except Exception as e:
            print(f"Error in content themes analysis: {e}")
            return ""
    
    def _format_sample_comments(self):
        """Format categorized sample comments for Gemini context"""
        if self.df is None or self.df.empty or 'textOriginal_cleaned' not in self.df.columns:
            return ""
        
        try:
            # Prepare different categories of comments
            categories = {
                'Highest Quality': self.df.sort_values('quality_score', ascending=False),
                'Most Positive': self.df[self.df['vader_sentiment'] == 'positive'].sort_values('vader_score', ascending=False),
                'Questions': self.df[self.df['engagement_type'] == 'question'],
                'Suggestions': self.df[self.df['engagement_type'] == 'suggestion'],
                'Product Inquiries': self.df[self.df['engagement_type'] == 'product_inquiry']
            }
            
            # Format the output
            comments_text = "SAMPLE COMMENTS BY CATEGORY:\n"
            
            for category, data in categories.items():
                if len(data) > 0:
                    comments = data['textOriginal_cleaned'].head(2).tolist()
                    if comments:
                        comments_text += f"\n{category}:\n"
                        for i, comment in enumerate(comments):
                            # Truncate long comments
                            if len(comment) > 100:
                                comment = comment[:97] + "..."
                            comments_text += f"{i+1}. {comment}\n"
            
            return comments_text
        except Exception as e:
            print(f"Error in sample comments formatting: {e}")
            return ""
    
    def _generate_recommendations_insight(self, insights):
        """Generate recommendations from actual data"""
        recommendations = []
        
        # Spam recommendations
        if insights.get('spam_rate', 0) > 15:
            recommendations.append("🛡️ **Spam Control:** Implement stricter comment moderation")
        
        # Quality recommendations
        if insights.get('avg_quality', 0) < 3:
            recommendations.append("📈 **Engagement:** Add clear call-to-actions to encourage meaningful comments")
        
        # Sentiment recommendations
        if insights.get('positive_rate', 0) < 50:
            recommendations.append("😊 **Positivity:** Create more engaging, positive content experiences")
        
        # Engagement recommendations
        top_engagement = insights.get('top_engagement', '')
        if top_engagement == 'question':
            recommendations.append("❓ **Q&A Content:** Your audience is curious - create FAQ or Q&A videos")
        elif top_engagement == 'technique_request':
            recommendations.append("🎓 **Tutorials:** High demand for educational content - focus on how-to videos")
        
        if not recommendations:
            recommendations.append("✅ **Keep Going:** Your metrics look good - maintain current strategy!")
        
        response = "💡 **Personalized Recommendations:**\n\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. {rec}\n"
        
        return response
    
    def _generate_trend_insight(self, insights):
        """Generate trend insights from actual data"""
        response = f"📈 **Key Trends Identified:**\n\n"
        
        # Quality trend
        avg_quality = insights.get('avg_quality', 0)
        if avg_quality > 3.5:
            response += f"📊 **Quality Trend:** High engagement quality ({avg_quality:.1f}/5)\n"
        
        # Engagement trend
        top_engagement = insights.get('top_engagement', 'general')
        response += f"🎯 **Engagement Trend:** Audience prefers {top_engagement.replace('_', ' ')} interactions\n"
        
        # Sentiment trend
        positive_rate = insights.get('positive_rate', 0)
        if positive_rate > 60:
            response += f"😊 **Sentiment Trend:** Strong positive audience response ({positive_rate:.1f}%)\n"
        
        # Community health
        spam_rate = insights.get('spam_rate', 0)
        genuine_rate = insights.get('genuine_rate', 0)
        if spam_rate < 10 and genuine_rate > 70:
            response += f"🌟 **Community Health:** Healthy, authentic community engagement\n"
        
        return response
    
    def _generate_content_insight(self, insights):
        """Generate content performance insights"""
        response = f"🎥 **Content Performance Analysis:**\n\n"
        
        avg_quality = insights.get('avg_quality', 0)
        positive_rate = insights.get('positive_rate', 0)
        
        response += f"• **Overall Performance:** "
        if avg_quality > 3.5 and positive_rate > 60:
            response += f"🌟 Excellent - High quality engagement with positive sentiment\n"
        elif avg_quality > 2.5 and positive_rate > 40:
            response += f"👍 Good - Solid performance with room for growth\n"
        else:
            response += f"📈 Opportunity - Focus on content that drives better engagement\n"
        
        # Engagement insights
        top_engagement = insights.get('top_engagement', 'general')
        response += f"• **Audience Preference:** {top_engagement.replace('_', ' ').title()} content\n"
        
        return response
    
    def _generate_general_insight(self, insights):
        """Generate general insights from actual data"""
        total = insights.get('total_comments', 0)
        avg_quality = insights.get('avg_quality', 0)
        positive_rate = insights.get('positive_rate', 0)
        spam_rate = insights.get('spam_rate', 0)
        
        response = f"📋 **Complete Analysis Overview:**\n\n"
        response += f"• **Dataset:** {total:,} comments analyzed\n"
        response += f"• **Quality Score:** {avg_quality:.1f}/5\n"
        response += f"• **Positive Sentiment:** {positive_rate:.1f}%\n"
        response += f"• **Spam Rate:** {spam_rate:.1f}%\n"
        
        response += f"\n**Summary:** "
        if avg_quality > 3.5 and spam_rate < 10:
            response += f"Your content generates high-quality, authentic engagement! 🌟"
        elif avg_quality > 2.5:
            response += f"Good engagement quality with opportunities for improvement. 👍"
        else:
            response += f"Focus on strategies to improve engagement quality and reduce spam. 📈"
        
        return response

    def _answer_spam_questions(self, question, context):
        """Answer spam-related questions"""
        spam_rate = self.context_data.get('spam_rate', 0)
        
        if spam_rate < 5:
            return f"Great news! Your spam rate is very low at {spam_rate:.1f}%. This indicates a healthy, authentic community. Your content attracts genuine engagement rather than spam or bot activity."
        elif spam_rate < 15:
            return f"Your spam rate is {spam_rate:.1f}%, which is within acceptable range. Consider monitoring for patterns and implementing community guidelines if it increases."
        else:
            return f"Your spam rate is {spam_rate:.1f}%, which is higher than ideal. I recommend implementing stricter comment moderation, community guidelines, and possibly using YouTube's automatic spam filtering features."
    
    def _answer_sentiment_questions(self, question, context):
        """Answer sentiment-related questions"""
        sentiment_dist = self.context_data.get('sentiment_dist', {})
        positive_rate = sentiment_dist.get('positive', 0) * 100
        negative_rate = sentiment_dist.get('negative', 0) * 100
        
        return f"Your sentiment analysis shows {positive_rate:.1f}% positive, {sentiment_dist.get('neutral', 0)*100:.1f}% neutral, and {negative_rate:.1f}% negative comments. " + \
               (f"Excellent positive sentiment! Your audience loves your content." if positive_rate > 60 else
                f"Good sentiment balance. Consider strategies to increase positive engagement." if positive_rate > 40 else
                f"There's room to improve sentiment. Focus on content that resonates better with your audience.")
    
    def _answer_engagement_questions(self, question, context):
        """Answer engagement-related questions"""
        engagement_dist = self.context_data.get('engagement_dist', {})
        top_engagement = max(engagement_dist.items(), key=lambda x: x[1]) if engagement_dist else ('general', 0)
        
        return f"Your top engagement type is '{top_engagement[0]}' at {top_engagement[1]*100:.1f}% of comments. " + \
               f"This suggests your audience is most likely to {top_engagement[0].replace('_', ' ')}. " + \
               f"Consider creating content that encourages this type of interaction."
    
    def _answer_quality_questions(self, question, context):
        """Answer quality-related questions"""
        avg_quality = self.context_data.get('avg_quality', 0)
        
        if avg_quality >= 4:
            return f"Excellent! Your average quality score is {avg_quality:.2f}/5. Your content generates high-quality, meaningful engagement from your audience."
        elif avg_quality >= 3:
            return f"Good quality engagement with a score of {avg_quality:.2f}/5. There's room for improvement - consider strategies to encourage more detailed, thoughtful comments."
        else:
            return f"Your quality score is {avg_quality:.2f}/5, indicating opportunities for improvement. Focus on creating content that encourages meaningful discussion and interaction."
    
    def _answer_strategy_questions(self, question, context):
        """Answer strategy and recommendation questions"""
        recommendations = self._generate_recommendations()
        if recommendations:
            return "Based on your data, here are my top recommendations:\n\n" + "\n".join(recommendations[:3])
        else:
            return "I need more data to provide specific recommendations. Try analyzing a larger dataset for better insights."
    
    def _answer_trend_questions(self, question, context):
        """Answer trend and pattern questions"""
        insights = self.generate_advanced_insights()
        if insights:
            return "Here are the key trends I've identified:\n\n" + "\n".join(insights[:3])
        else:
            return "I need more data to identify meaningful trends. Upload a larger dataset for better pattern analysis."
    
    def _answer_content_questions(self, question, context):
        """Answer content performance questions"""
        if 'title' in self.df.columns and 'quality_score' in self.df.columns:
            video_performance = self.df.groupby('title')['quality_score'].mean().sort_values(ascending=False)
            if len(video_performance) > 0:
                best_video = video_performance.index[0]
                best_score = video_performance.iloc[0]
                return f"Your best performing content is '{best_video[:50]}...' with a quality score of {best_score:.2f}/5. Analyze this content style for future videos."
        
        return "To analyze content performance, I need video titles in your dataset. Make sure your videos.csv file includes a 'title' column."
    
    def _answer_general_questions(self, question, context):
        """Answer general questions"""
        total_comments = self.context_data.get('total_comments', 0)
        
        return f"I've analyzed {total_comments:,} comments from your dataset. " + \
               f"You can ask me about spam rates, sentiment analysis, engagement patterns, quality scores, " + \
               f"content performance, or recommendations for improvement. What would you like to know more about?"

    def generate_ai_summary(self):
        """Generate an AI-powered executive summary"""
        if self.df is None or self.df.empty:
            return "No data available for AI summary."
        
        # Collect key metrics
        total_comments = len(self.df)
        spam_rate = (self.df.get('is_spam', pd.Series()) == True).mean() * 100
        avg_quality = self.df.get('quality_score', pd.Series()).mean()
        sentiment_dist = self.df.get('vader_sentiment', pd.Series()).value_counts(normalize=True)
        
        # Generate narrative summary
        summary = f"""
        🤖 **AI Executive Summary**
        
        **Dataset Overview:** Analyzed {total_comments:,} YouTube comments with AI-powered classification.
        
        **Community Health:** {'Excellent' if spam_rate < 5 else 'Good' if spam_rate < 15 else 'Needs Attention'} 
        (Spam Rate: {spam_rate:.1f}%)
        
        **Engagement Quality:** {'High' if avg_quality >= 3.5 else 'Moderate' if avg_quality >= 2.5 else 'Low'} 
        (Quality Score: {avg_quality:.2f}/5)
        
        **Audience Sentiment:** {sentiment_dist.index[0].title()} dominant 
        ({sentiment_dist.iloc[0]*100:.1f}% of comments)
        
        **Key Insight:** {self._get_key_insight()}
        
        **Priority Action:** {self._get_priority_action()}
        """
        
        return summary
    
    def _get_key_insight(self):
        """Generate the most important insight"""
        if 'engagement_type' in self.df.columns:
            top_engagement = self.df['engagement_type'].value_counts().index[0]
            if top_engagement == 'question':
                return "Your audience is highly curious and engaged - leverage this with Q&A content."
            elif top_engagement == 'technique_request':
                return "Strong demand for educational content - focus on tutorial-style videos."
            elif top_engagement == 'praise':
                return "Excellent audience satisfaction - maintain current content quality."
        
        return "Audience shows mixed engagement patterns - analyze top-performing content for insights."
    
    def _get_priority_action(self):
        """Generate the top priority action"""
        spam_rate = self.context_data.get('spam_rate', 0)
        avg_quality = self.context_data.get('avg_quality', 0)
        
        if spam_rate > 20:
            return "Implement stronger community moderation to reduce spam."
        elif avg_quality < 2:
            return "Focus on content that encourages meaningful audience interaction."
        elif avg_quality >= 4:
            return "Maintain current strategy and consider scaling successful content themes."
        else:
            return "Optimize call-to-actions to increase engagement quality."
    
    def get_real_time_insight(self):
        """Generate a real-time insight for the chat bubble"""
        if self.df is None or self.df.empty:
            return "Upload data to get AI insights!"
        
        insights = [
            f"📊 Analyzed {len(self.df):,} comments",
            f"🎯 {(self.df.get('relevance', pd.Series()) == 'genuine').mean()*100:.0f}% genuine engagement",
            f"⭐ Average quality score: {self.df.get('quality_score', pd.Series()).mean():.1f}/5",
            f"😊 {(self.df.get('vader_sentiment', pd.Series()) == 'positive').mean()*100:.0f}% positive sentiment"
        ]
        
        return " • ".join(insights)
    
    def get_quick_stats(self):
        """Get quick statistics for display"""
        if self.df is None or self.df.empty:
            return {}
        
        return {
            'total_comments': len(self.df),
            'spam_rate': (self.df.get('is_spam', pd.Series()) == True).mean() * 100,
            'quality_score': self.df.get('quality_score', pd.Series()).mean(),
            'positive_sentiment': (self.df.get('vader_sentiment', pd.Series()) == 'positive').mean() * 100,
            'genuine_rate': (self.df.get('relevance', pd.Series()) == 'genuine').mean() * 100
        }
    
    def get_ai_status(self):
        """Get AI system status"""
        return {
            'gemini_available': GEMINI_AVAILABLE,
            'gemini_enabled': self.is_gemini_enabled,
            'api_key_configured': AIConfig.is_configured(),
            'model': AIConfig.GEMINI_MODEL if self.is_gemini_enabled else 'Rule-based fallback'
        }
    
    def get_setup_instructions(self):
        """Get setup instructions for AI"""
        if self.is_gemini_enabled:
            return "✅ Gemini AI is active and ready to answer your questions!"
        else:
            return AIConfig.get_api_key_instructions()
    
    def generate_smart_insights(self, question_type="general"):
        """Generate smart insights using Gemini"""
        if not self.is_gemini_enabled:
            return self.generate_advanced_insights()
        
        try:
            data_context = self._prepare_gemini_context()
            
            prompts = {
                "general": "Provide 3-5 key insights about this YouTube comment data that would be most valuable for a content creator.",
                "strategy": "Based on this comment analysis, what are the top 3 strategic recommendations for improving content and engagement?",
                "audience": "What does this comment data reveal about the audience behavior and preferences?",
                "performance": "Analyze the content performance based on these comments and suggest improvements."
            }
            
            prompt = f"""
            {AIConfig.SYSTEM_PROMPT}
            
            DATA CONTEXT:
            {data_context}
            
            TASK: {prompts.get(question_type, prompts["general"])}
            
            Please provide specific, actionable insights based on the actual data.
            Format as bullet points for easy reading.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return [response.text]
            
        except Exception as e:
            print(f"Gemini insights error: {e}")
            return self.generate_advanced_insights()