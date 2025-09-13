"""
Dashboard and visualization module for comment analysis results
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CommentDashboard:
    def __init__(self, df):
        self.df = df
        plt.style.use('seaborn-v0_8')
        
    def create_overview_stats(self):
        """Create overview statistics"""
        stats = {
            'total_comments': len(self.df),
            'avg_quality_score': self.df.get('quality_score', pd.Series()).mean(),
            'spam_percentage': (self.df.get('is_spam', pd.Series()) == True).mean() * 100,
            'top_engagement_type': self.df.get('engagement_type', pd.Series()).mode().iloc[0] if not self.df.empty else 'N/A'
        }
        return stats
    
    def plot_relevance_distribution(self):
        """Plot distribution of comment relevance"""
        if 'relevance' not in self.df.columns:
            return None
            
        fig, ax = plt.subplots(figsize=(10, 6))
        relevance_counts = self.df['relevance'].value_counts()
        
        colors = {'genuine': '#2E8B57', 'general': '#4682B4', 'spam': '#DC143C'}
        bars = ax.bar(relevance_counts.index, relevance_counts.values, 
                     color=[colors.get(x, '#808080') for x in relevance_counts.index])
        
        ax.set_title('Comment Relevance Distribution', fontsize=16, fontweight='bold')
        ax.set_xlabel('Relevance Category')
        ax.set_ylabel('Number of Comments')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def plot_sentiment_analysis(self):
        """Plot sentiment analysis results"""
        if 'vader_sentiment' not in self.df.columns:
            return None
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Sentiment distribution
        sentiment_counts = self.df['vader_sentiment'].value_counts()
        colors = {'positive': '#32CD32', 'neutral': '#FFD700', 'negative': '#FF6347'}
        
        ax1.pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%',
               colors=[colors.get(x, '#808080') for x in sentiment_counts.index])
        ax1.set_title('Sentiment Distribution')
        
        # Sentiment scores distribution
        if 'vader_score' in self.df.columns:
            ax2.hist(self.df['vader_score'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax2.set_title('Sentiment Score Distribution')
            ax2.set_xlabel('VADER Sentiment Score')
            ax2.set_ylabel('Frequency')
            ax2.axvline(x=0, color='red', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        return fig
    
    def plot_engagement_types(self):
        """Plot engagement type distribution"""
        if 'engagement_type' not in self.df.columns:
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        engagement_counts = self.df['engagement_type'].value_counts()
        
        bars = ax.bar(range(len(engagement_counts)), engagement_counts.values, 
                     color='lightcoral', alpha=0.8)
        ax.set_xticks(range(len(engagement_counts)))
        ax.set_xticklabels(engagement_counts.index, rotation=45, ha='right')
        ax.set_title('Engagement Type Distribution', fontsize=16, fontweight='bold')
        ax.set_ylabel('Number of Comments')
        
        # Add value labels
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def plot_quality_vs_likes(self):
        """Plot quality score vs like count correlation"""
        if 'quality_score' not in self.df.columns or 'likeCount' not in self.df.columns:
            return None
            
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Filter out extreme outliers for better visualization
        df_filtered = self.df[self.df['likeCount'] <= self.df['likeCount'].quantile(0.95)]
        
        scatter = ax.scatter(df_filtered['quality_score'], df_filtered['likeCount'], 
                           alpha=0.6, c='steelblue')
        
        ax.set_xlabel('Quality Score')
        ax.set_ylabel('Like Count')
        ax.set_title('Comment Quality vs Like Count')
        
        # Add trend line
        z = np.polyfit(df_filtered['quality_score'], df_filtered['likeCount'], 1)
        p = np.poly1d(z)
        ax.plot(df_filtered['quality_score'], p(df_filtered['quality_score']), 
               "r--", alpha=0.8, linewidth=2)
        
        plt.tight_layout()
        return fig
    
    def create_interactive_dashboard(self):
        """Create interactive Plotly dashboard"""
        if self.df.empty:
            return None
            
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Relevance Distribution', 'Sentiment Analysis', 
                          'Engagement Types', 'Quality Scores'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "bar"}, {"type": "histogram"}]]
        )
        
        # Relevance distribution
        if 'relevance' in self.df.columns:
            relevance_counts = self.df['relevance'].value_counts()
            fig.add_trace(
                go.Bar(x=relevance_counts.index, y=relevance_counts.values, 
                      name="Relevance", showlegend=False),
                row=1, col=1
            )
        
        # Sentiment pie chart
        if 'vader_sentiment' in self.df.columns:
            sentiment_counts = self.df['vader_sentiment'].value_counts()
            fig.add_trace(
                go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values,
                      name="Sentiment", showlegend=False),
                row=1, col=2
            )
        
        # Engagement types
        if 'engagement_type' in self.df.columns:
            engagement_counts = self.df['engagement_type'].value_counts()
            fig.add_trace(
                go.Bar(x=engagement_counts.index, y=engagement_counts.values,
                      name="Engagement", showlegend=False),
                row=2, col=1
            )
        
        # Quality score distribution
        if 'quality_score' in self.df.columns:
            fig.add_trace(
                go.Histogram(x=self.df['quality_score'], name="Quality", showlegend=False),
                row=2, col=2
            )
        
        fig.update_layout(height=800, title_text="Comment Analysis Dashboard")
        return fig
    
    def generate_insights(self):
        """Generate AI-like insights and recommendations"""
        insights = []
        
        if self.df.empty:
            return ["No data available for analysis"]
        
        # Spam analysis
        if 'is_spam' in self.df.columns:
            spam_rate = (self.df['is_spam'] == True).mean() * 100
            if spam_rate > 20:
                insights.append(f"⚠️ High spam rate detected ({spam_rate:.1f}%). Consider implementing stricter comment moderation.")
            elif spam_rate < 5:
                insights.append(f"✅ Low spam rate ({spam_rate:.1f}%) indicates good community engagement.")
        
        # Sentiment analysis
        if 'vader_sentiment' in self.df.columns:
            sentiment_dist = self.df['vader_sentiment'].value_counts(normalize=True) * 100
            if sentiment_dist.get('positive', 0) > 60:
                insights.append("😊 Highly positive community sentiment - content is well-received!")
            elif sentiment_dist.get('negative', 0) > 30:
                insights.append("😟 High negative sentiment detected. Review recent content for potential issues.")
        
        # Engagement analysis
        if 'engagement_type' in self.df.columns:
            top_engagement = self.df['engagement_type'].mode().iloc[0]
            if top_engagement == 'question':
                insights.append("❓ Many viewers are asking questions - consider creating FAQ content or tutorials.")
            elif top_engagement == 'technique_request':
                insights.append("🎯 High demand for technique tutorials - great opportunity for educational content.")
        
        # Quality analysis
        if 'quality_score' in self.df.columns:
            avg_quality = self.df['quality_score'].mean()
            if avg_quality > 3:
                insights.append("⭐ High average comment quality indicates strong audience engagement.")
            elif avg_quality < 1.5:
                insights.append("📈 Consider strategies to encourage more meaningful interactions.")
        
        return insights if insights else ["Analysis complete - no specific recommendations at this time."]

if __name__ == "__main__":
    # Example usage with sample data
    sample_data = pd.DataFrame({
        'relevance': ['genuine', 'spam', 'general', 'genuine', 'general'],
        'vader_sentiment': ['positive', 'neutral', 'positive', 'negative', 'positive'],
        'engagement_type': ['question', 'general', 'praise', 'suggestion', 'thanks'],
        'quality_score': [4, 0, 2, 3, 2],
        'likeCount': [5, 0, 2, 8, 1],
        'is_spam': [False, True, False, False, False]
    })
    
    dashboard = CommentDashboard(sample_data)
    insights = dashboard.generate_insights()
    
    print("Generated Insights:")
    for insight in insights:
        print(f"- {insight}")