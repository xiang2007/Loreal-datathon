"""
AI Assistant for L'Oréal Comment Analysis
Provides advanced insights and interactive Q&A
"""
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
from collections import Counter
import json

class AIAssistant:
    def __init__(self, df=None):
        self.df = df
        self.context_data = {}
        if df is not None:
            self._prepare_context()
    
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
        """AI assistant to answer questions about the analysis"""
        question_lower = question.lower()
        
        if self.df is None or self.df.empty:
            return "I don't have any data to analyze yet. Please upload and analyze your CSV files first!"
        
        # Prepare context summary
        context = self._get_context_summary()
        
        # Question routing based on keywords
        if any(word in question_lower for word in ['spam', 'fake', 'bot']):
            return self._answer_spam_questions(question_lower, context)
        
        elif any(word in question_lower for word in ['sentiment', 'positive', 'negative', 'emotion']):
            return self._answer_sentiment_questions(question_lower, context)
        
        elif any(word in question_lower for word in ['engagement', 'interact', 'participate']):
            return self._answer_engagement_questions(question_lower, context)
        
        elif any(word in question_lower for word in ['quality', 'score', 'rating']):
            return self._answer_quality_questions(question_lower, context)
        
        elif any(word in question_lower for word in ['recommend', 'suggest', 'improve', 'strategy']):
            return self._answer_strategy_questions(question_lower, context)
        
        elif any(word in question_lower for word in ['trend', 'pattern', 'insight']):
            return self._answer_trend_questions(question_lower, context)
        
        elif any(word in question_lower for word in ['video', 'content', 'performance']):
            return self._answer_content_questions(question_lower, context)
        
        else:
            return self._answer_general_questions(question_lower, context)
    
    def _get_context_summary(self):
        """Get a summary of the current analysis context"""
        if not self.context_data:
            return "No analysis data available."
        
        return f"""
        Analysis Summary:
        - Total Comments: {self.context_data.get('total_comments', 0):,}
        - Spam Rate: {self.context_data.get('spam_rate', 0):.1f}%
        - Average Quality Score: {self.context_data.get('avg_quality', 0):.2f}/5
        - Sentiment Distribution: {self.context_data.get('sentiment_dist', {})}
        - Top Engagement Types: {self.context_data.get('engagement_dist', {})}
        """
    
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