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
        """Initialize Gemini AI model"""
        if not GEMINI_AVAILABLE:
            print("⚠️ Gemini not available - missing dependencies")
            return
        
        try:
            api_key = AIConfig.GEMINI_API_KEY
            print(f"🔍 API Key status: {'Found' if api_key else 'Not found'}")
            if api_key:
                print(f"🔑 API Key (first 10 chars): {api_key[:10]}...")
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel(AIConfig.GEMINI_MODEL)
                self.is_gemini_enabled = True
                print("✅ Gemini AI initialized successfully")
            else:
                print("⚠️ Gemini API key not found in environment variables")
                print("💡 Make sure GEMINI_API_KEY is set in your .env file")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini: {e}")
            self.is_gemini_enabled = False
    
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
    
    def _answer_with_gemini(self, question):
        """Answer questions using Gemini AI"""
        try:
            # Prepare data context for Gemini
            data_context = self._prepare_gemini_context()
            
            # Create the prompt
            prompt = f"""
            {AIConfig.SYSTEM_PROMPT}
            
            DATA CONTEXT:
            {data_context}
            
            USER QUESTION: {question}
            
            Please provide a helpful, specific answer based on the actual data provided above.
            Include specific numbers and percentages where relevant.
            Give actionable recommendations when appropriate.
            Keep the response conversational and easy to understand.
            """
            
            # Generate response
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=AIConfig.MAX_TOKENS,
                    temperature=AIConfig.TEMPERATURE,
                )
            )
            
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            print(f"Gemini error: {e}")
            
            # Check if it's a quota error
            if "quota" in error_msg.lower() or "429" in error_msg:
                fallback_response = self._answer_with_rules(question)
                return f"🤖 **AI Assistant** (Data-driven analysis):\n\n{fallback_response}\n\n" + \
                       f"💡 *Note: Using enhanced data analysis due to API limits. Upgrade your Gemini plan for full AI responses.*"
            else:
                # Other errors - use fallback
                return self._answer_with_rules(question)
    
    def _prepare_gemini_context(self):
        """Prepare comprehensive data context for Gemini"""
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
        
        # Video performance (if available)
        video_performance = ""
        if 'title' in self.df.columns:
            video_stats = self.df.groupby('title').agg({
                'quality_score': 'mean',
                'textOriginal_cleaned': 'count'
            }).round(2)
            video_stats.columns = ['Avg_Quality', 'Comment_Count']
            video_stats = video_stats.sort_values('Avg_Quality', ascending=False)
            
            video_performance = f"""
VIDEO PERFORMANCE:
Top 3 performing videos by quality:
{video_stats.head(3).to_string()}
"""
        
        # Sample comments for context
        sample_comments = ""
        if 'textOriginal_cleaned' in self.df.columns:
            genuine_comments = self.df[self.df.get('relevance', '') == 'genuine']['textOriginal_cleaned'].dropna()
            if len(genuine_comments) > 0:
                sample_comments = f"""
SAMPLE GENUINE COMMENTS:
{genuine_comments.head(5).tolist()}
"""
        
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

ENGAGEMENT TYPES:
- Praise/Compliments: {engagement_dist.get('praise', 0):.1f}%
- Questions: {engagement_dist.get('question', 0):.1f}%
- Technique Requests: {engagement_dist.get('technique_request', 0):.1f}%
- General Comments: {engagement_dist.get('general', 0):.1f}%
- Product Inquiries: {engagement_dist.get('product_inquiry', 0):.1f}%

{video_performance}

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