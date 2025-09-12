"""
Test script to demonstrate the AI Assistant bubble functionality
"""
import streamlit as st
import pandas as pd
import sys
sys.path.append('src')

from src.ai_assistant import AIAssistant

# Page config
st.set_page_config(
    page_title="AI Assistant Demo",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for the chat bubble
st.markdown("""
<style>
    .chat-bubble-demo {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #E31837, #ff4757);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(227, 24, 55, 0.3);
        z-index: 1000;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .chat-bubble-demo:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(227, 24, 55, 0.4);
    }
    
    .demo-message {
        background: linear-gradient(135deg, #E31837, #ff4757);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .user-message-demo {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #E31837;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 AI Assistant Demo")
st.markdown("This demonstrates how the AI assistant bubble will work with your comment analysis data.")

# Create sample data for demo
if 'demo_data' not in st.session_state:
    # Create sample analyzed data
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
    
    st.session_state.demo_data = pd.DataFrame(sample_data)

# Initialize AI Assistant with demo data
ai_assistant = AIAssistant(st.session_state.demo_data)

# Show AI status
ai_status = ai_assistant.get_ai_status()
if ai_status['gemini_enabled']:
    st.success("🤖 Powered by Google Gemini AI")
else:
    st.warning("⚠️ Gemini not configured - using basic AI")
    with st.expander("🔧 Setup Gemini AI", expanded=False):
        st.code(ai_assistant.get_setup_instructions())

# Demo interface
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Interactive AI Chat")
    
    # Initialize chat history
    if 'demo_chat' not in st.session_state:
        st.session_state.demo_chat = []
    
    # Display chat
    for question, answer in st.session_state.demo_chat:
        st.markdown(f"""
        <div class="user-message-demo">
            <strong>🙋 You:</strong> {question}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="demo-message">
            <strong>🤖 AI Assistant:</strong> {answer}
        </div>
        """, unsafe_allow_html=True)
    
    # Question input
    user_question = st.text_input("Ask the AI assistant about your data:", 
                                 placeholder="e.g., What's my spam rate?")
    
    col_a, col_b = st.columns([1, 4])
    with col_a:
        if st.button("Ask AI", type="primary"):
            if user_question:
                answer = ai_assistant.answer_question(user_question)
                st.session_state.demo_chat.append((user_question, answer))
                st.rerun()
    
    with col_b:
        if st.button("Clear Chat"):
            st.session_state.demo_chat = []
            st.rerun()

with col2:
    st.subheader("📊 Quick Stats")
    
    stats = ai_assistant.get_quick_stats()
    
    st.metric("Total Comments", f"{stats.get('total_comments', 0):,}")
    st.metric("Spam Rate", f"{stats.get('spam_rate', 0):.1f}%")
    st.metric("Quality Score", f"{stats.get('quality_score', 0):.1f}/5")
    st.metric("Positive Sentiment", f"{stats.get('positive_sentiment', 0):.1f}%")
    
    st.markdown("---")
    
    st.subheader("⚡ Quick Questions")
    quick_questions = [
        "What's my spam rate and how can I improve it?",
        "Analyze my audience sentiment and engagement",
        "Give me 3 actionable recommendations",
        "What content strategy should I focus on?",
        "How can I increase comment quality?",
        "What do my viewers want to see more of?"
    ]
    
    for question in quick_questions:
        if st.button(f"💭 {question}", key=f"quick_{question}", use_container_width=True):
            answer = ai_assistant.answer_question(question)
            st.session_state.demo_chat.append((question, answer))
            st.rerun()

# Floating chat bubble (demo)
st.markdown("""
<div class="chat-bubble-demo" title="AI Assistant - Click to chat!">
    <div style="color: white; font-size: 24px;">🤖</div>
</div>
""", unsafe_allow_html=True)

# Instructions
st.markdown("---")
st.markdown("""
### 🎯 How the AI Assistant Works:

1. **Floating Bubble**: The AI assistant appears as a floating bubble in the bottom-right corner
2. **Smart Analysis**: It analyzes your comment data and provides insights
3. **Natural Conversation**: Ask questions in plain English about your data
4. **Quick Actions**: Get instant insights with pre-built quick questions
5. **Contextual Responses**: The AI understands your specific data and provides relevant answers

**Try asking questions like:**
- "What's my spam rate and how can I improve it?"
- "How is my audience sentiment?"
- "Give me recommendations for better engagement"
- "What trends do you see in my comments?"
""")