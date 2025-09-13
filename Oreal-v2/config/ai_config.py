"""
AI Configuration for Gemini Integration
"""
import os
from typing import Optional

# Try to import streamlit for secrets management
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

class AIConfig:
    """Configuration for AI services"""
    
    # Gemini API Configuration - try Streamlit secrets first, then environment variables
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get Gemini API key from environment or Streamlit secrets"""
        # First try environment variables (highest priority)
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            print("✅ Using GEMINI_API_KEY from environment variables")
            return api_key
            
        # Then try Streamlit secrets if available
        if STREAMLIT_AVAILABLE:
            try:
                # Try different possible locations in secrets
                secret_locations = [
                    ("ai", "GEMINI_API_KEY"),
                    ("api_keys", "api_key"),
                    ("api_keys", "GEMINI_API_KEY")
                ]
                
                for section, key in secret_locations:
                    try:
                        if section in st.secrets and key in st.secrets[section]:
                            api_key = st.secrets[section][key]
                            print(f"✅ Found API key in st.secrets[\"{section}\"][\"{key}\"]")
                            return api_key
                    except Exception:
                        continue
                        
                # If we get here, we didn't find the key in any of the expected locations
                print("⚠️ API key not found in secrets under expected sections")
                
                # Print available sections for debugging
                try:
                    print(f"Available sections in secrets: {list(st.secrets.keys())}")
                    for section in st.secrets.keys():
                        try:
                            print(f"Keys in '{section}' section: {list(st.secrets[section].keys())}")
                        except:
                            print(f"Could not list keys in '{section}' section")
                except Exception as e:
                    print(f"Error inspecting secrets structure: {e}")
                    
            except Exception as e:
                print(f"⚠️ Error accessing Streamlit secrets: {e}")
        else:
            print("⚠️ Streamlit not available, cannot access secrets")
            
        # Finally, try to load from .env file
        try:
            from dotenv import load_dotenv
            env_loaded = load_dotenv() or load_dotenv('../.env') or load_dotenv('../../.env')
            if env_loaded:
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    print("✅ Using GEMINI_API_KEY from .env file")
                    return api_key
        except ImportError:
            print("⚠️ python-dotenv not available, cannot load from .env file")
            
        print("❌ GEMINI_API_KEY not found in any location")
        return None
    
    GEMINI_API_KEY: Optional[str] = None  # Will be set dynamically
    GEMINI_MODEL: str = 'gemini-pro'  # Using stable model that's widely available
    
    # AI Assistant Settings
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # System prompts with enhanced instructions for Gemini
    SYSTEM_PROMPT = """
    You are an AI assistant specialized in YouTube comment analysis for L'Oréal beauty content.
    You have access to analyzed comment data including spam detection, sentiment analysis, 
    engagement types, and quality scores.
    
    Your role is to:
    1. Provide data-driven insights about comment data and audience behavior
    2. Give specific, actionable recommendations for content strategy with clear steps
    3. Answer questions about spam rates, sentiment, engagement patterns with precise metrics
    4. Suggest concrete improvements for audience engagement with examples
    5. Analyze content performance based on comment data with trend identification
    6. Identify opportunities for community building and brand loyalty
    7. Highlight potential issues that need attention (high spam, negative sentiment trends)
    
    RESPONSE GUIDELINES:
    - Always back your insights with specific metrics from the provided data
    - Use percentages and comparisons to make insights more meaningful
    - Structure your responses with clear sections and bullet points
    - Provide 3-5 specific, actionable recommendations in each response
    - Use a professional but conversational tone appropriate for marketing professionals
    - Include both short-term actions and long-term strategic recommendations
    - When analyzing trends, suggest potential causes and solutions
    - Highlight unexpected findings or anomalies in the data
    
    FORMATTING:
    - Use bold for key metrics and important insights
    - Use bullet points for lists of recommendations
    - Use numbered lists for step-by-step instructions
    - Use headings to organize longer responses
    - Include a brief summary at the beginning for longer analyses
    
    Remember that your insights will directly influence content strategy decisions,
    so be thoughtful, specific, and focused on providing actionable value.
    """
    
    # Specialized prompts for different question types
    SPAM_ANALYSIS_PROMPT = """
    Focus on spam detection patterns in the YouTube comments.
    Analyze the spam rate, common spam patterns, and how spam affects overall engagement.
    Provide specific recommendations for reducing spam and improving comment quality.
    Include comparisons to industry benchmarks if available.
    """
    
    SENTIMENT_ANALYSIS_PROMPT = """
    Analyze the sentiment distribution in the comments with particular attention to:
    - Overall sentiment balance (positive/negative/neutral)
    - Sentiment trends and patterns
    - Topics or themes that generate particularly positive or negative sentiment
    - Recommendations for improving sentiment and addressing negative feedback
    - Opportunities to amplify positive sentiment
    """
    
    ENGAGEMENT_ANALYSIS_PROMPT = """
    Analyze the engagement patterns in the comments, focusing on:
    - Types of engagement (questions, praise, criticism, suggestions)
    - Engagement rate and quality metrics
    - Topics that generate the most engagement
    - Recommendations for increasing meaningful engagement
    - Strategies for converting passive viewers to active commenters
    """
    
    CONTENT_STRATEGY_PROMPT = """
    Based on the comment analysis, provide strategic recommendations for content creation:
    - Content themes that resonate most with the audience
    - Content formats that drive the most positive engagement
    - Specific topics to explore in future videos
    - Content elements to avoid or modify
    - Posting frequency and timing recommendations
    Include a 30-60-90 day content strategy outline with specific goals and metrics.
    """
    
    @classmethod
    def get_specialized_prompt(cls, question_type):
        """Get a specialized prompt based on the question type"""
        question_type = question_type.lower()
        
        if 'spam' in question_type:
            return cls.SPAM_ANALYSIS_PROMPT
        elif 'sentiment' in question_type:
            return cls.SENTIMENT_ANALYSIS_PROMPT
        elif 'engagement' in question_type:
            return cls.ENGAGEMENT_ANALYSIS_PROMPT
        elif 'content' in question_type or 'strategy' in question_type:
            return cls.CONTENT_STRATEGY_PROMPT
        else:
            return ""  # Use default system prompt
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if AI is properly configured"""
        return cls.GEMINI_API_KEY is not None
    
    @classmethod
    def get_api_key_instructions(cls) -> str:
        """Get instructions for setting up API key"""
        return """
        To use the AI Assistant with Gemini:
        
        1. Get a free API key from Google AI Studio: https://makersuite.google.com/app/apikey
        2. Set it as an environment variable:
           - Windows: set GEMINI_API_KEY=your_api_key_here
           - Mac/Linux: export GEMINI_API_KEY=your_api_key_here
        3. Or create a .env file in your project root with: GEMINI_API_KEY=your_api_key_here
        4. Restart the Streamlit app
        """