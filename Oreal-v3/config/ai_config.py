"""
AI Configuration for Gemini Integration
"""
import os
from typing import Optional

class AIConfig:
    """Configuration for AI services"""
    
    # Gemini API Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL: str = 'gemini-1.5-flash'  # or 'gemini-1.5-pro' for more advanced features
    
    # AI Assistant Settings
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # System prompts
    SYSTEM_PROMPT = """
    You are an AI assistant specialized in YouTube comment analysis for L'Oréal beauty content.
    You have access to analyzed comment data including spam detection, sentiment analysis, 
    engagement types, and quality scores.
    
    Your role is to:
    1. Provide insights about comment data and audience behavior
    2. Give actionable recommendations for content strategy
    3. Answer questions about spam rates, sentiment, engagement patterns
    4. Suggest improvements for audience engagement
    5. Analyze content performance based on comment data
    
    Always be helpful, specific, and provide actionable advice.
    Use the actual data provided to give accurate insights.
    """
    
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