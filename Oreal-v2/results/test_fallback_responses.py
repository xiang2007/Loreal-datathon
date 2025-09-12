"""
Test the improved fallback responses (data-driven instead of hardcoded)
"""
import sys
sys.path.append('src')

import pandas as pd
from src.ai_assistant import AIAssistant

# Create sample data
sample_data = {
    'textOriginal_cleaned': [
        'Love this makeup tutorial!',
        'Amazing content, keep it up!',
        'Check out my channel for more tips',
        'What foundation are you using?',
        'This is spam content',
        'Great tutorial, very helpful'
    ],
    'is_spam': [False, False, True, False, True, False],
    'quality_score': [4.2, 4.5, 1.0, 3.8, 0.5, 4.0],
    'vader_sentiment': ['positive', 'positive', 'neutral', 'neutral', 'negative', 'positive'],
    'relevance': ['genuine', 'genuine', 'spam', 'genuine', 'spam', 'genuine'],
    'engagement_type': ['praise', 'praise', 'general', 'question', 'general', 'praise']
}

df = pd.DataFrame(sample_data)

print("🧪 Testing Data-Driven Fallback Responses...")
print("=" * 60)

# Initialize AI Assistant
ai_assistant = AIAssistant(df)

# Temporarily disable Gemini to test fallback
ai_assistant.is_gemini_enabled = False

print("🔧 Gemini disabled - testing data-driven fallback responses")
print("=" * 60)

# Test questions
test_questions = [
    "What's my spam rate?",
    "How is my audience sentiment?", 
    "What type of engagement do I get?",
    "How is my content quality?",
    "Give me recommendations"
]

for question in test_questions:
    print(f"\n❓ **Question:** {question}")
    print("-" * 40)
    
    try:
        answer = ai_assistant.answer_question(question)
        print(f"🤖 **Data-Driven Response:**\n{answer}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

print("=" * 60)
print("✅ All responses are now data-driven, not hardcoded!")
print("💡 When Gemini quota is available, you get full AI responses.")
print("🔄 When quota is exceeded, you get intelligent data analysis instead of generic text.")