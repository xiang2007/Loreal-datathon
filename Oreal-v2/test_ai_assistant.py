"""
Test the AI Assistant with API key
"""
import sys
sys.path.append('src')

from dotenv import load_dotenv
load_dotenv()

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

print("🧪 Testing AI Assistant...")
print("=" * 50)

# Initialize AI Assistant
ai_assistant = AIAssistant(df)

# Check status
status = ai_assistant.get_ai_status()
print(f"🤖 Gemini Available: {status['gemini_available']}")
print(f"🔑 API Key Configured: {status['api_key_configured']}")
print(f"✅ Gemini Enabled: {status['gemini_enabled']}")
print(f"🎯 Model: {status['model']}")

print("\n" + "=" * 50)

# Test questions
test_questions = [
    "What's my spam rate?",
    "How is my audience sentiment?",
    "Give me recommendations"
]

for question in test_questions:
    print(f"\n❓ Question: {question}")
    print("-" * 30)
    
    try:
        answer = ai_assistant.answer_question(question)
        print(f"🤖 Answer: {answer}")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Test completed!")