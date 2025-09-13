"""
Streamlit Web Application for L'Oréal YouTube Comment Quality Analysis
"""
# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Environment variables loaded in Streamlit app")
except ImportError:
    print("⚠️ python-dotenv not available")
    pass

import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import sys
import tempfile
import zipfile
import gc
import psutil
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add src directory to path
sys.path.append('src')

# Import large dataset configurations
try:
    from config.large_dataset_config import *
except ImportError:
    # Fallback configuration if file not found
    LARGE_DATASET_CONFIG = {
        'batch_sizes': {'small': 250, 'medium': 500, 'large': 1000, 'xlarge': 2000},
        'sampling': {'enable_sampling_above': 100000}
    }

try:
    from src.data_processing import DataProcessor
    from src.enhanced_analysis import EnhancedCommentAnalyzer as CommentAnalyzer
    from src.dashboard import CommentDashboard
    from src.ai_assistant import AIAssistant
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="L'Oréal YouTube Comment Analysis",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set session state to ensure sidebar visibility
if 'sidebar_state' not in st.session_state:
    st.session_state.sidebar_state = 'expanded'

# Enhanced Custom CSS for Modern UI/UX
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #E31837, #ff6b7a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Sidebar Styling - Force sidebar to stay visible */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        min-width: 300px !important;
        width: 300px !important;
        position: relative !important;
        transform: none !important;
        transition: none !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        border-radius: 0 16px 16px 0;
    }
    
    /* Target all sidebar containers with various class names */
    .css-1d391kg, .css-1lcbmhc, .css-1cypcdb, .css-17eq0hr, .css-1544g2n, .css-1fcdlhc, .css-1vq4p4l {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        min-width: 300px !important;
        width: 300px !important;
        position: relative !important;
        transform: none !important;
        transition: none !important;
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Hide sidebar collapse button */
    [data-testid="collapsedControl"], .css-1rs6os, .css-hied5v {
        display: none !important;
    }
    
    /* Force sidebar visibility on all screen sizes */
    @media (max-width: 768px) {
        [data-testid="stSidebar"], .css-1d391kg, .css-1lcbmhc, .css-1cypcdb, .css-17eq0hr, .css-1544g2n, .css-1fcdlhc, .css-1vq4p4l {
            display: block !important;
            position: relative !important;
            transform: none !important;
            min-width: 280px !important;
            width: 280px !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e9ecef;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #E31837, #ff6b7a);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(227, 24, 55, 0.15);
    }
    
    /* Insight Boxes */
    .insight-box {
        background: linear-gradient(135deg, #e8f4fd, #f0f8ff);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(31, 119, 180, 0.1);
    }
    
    .insight-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #1f77b4, #4dabf7);
    }
    
    /* Chat Bubble */
    .chat-bubble {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #E31837, #ff4757);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 8px 25px rgba(227, 24, 55, 0.4);
        z-index: 1000;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 8px 25px rgba(227, 24, 55, 0.4); }
        50% { box-shadow: 0 8px 35px rgba(227, 24, 55, 0.6); }
        100% { box-shadow: 0 8px 25px rgba(227, 24, 55, 0.4); }
    }
    
    .chat-bubble:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 40px rgba(227, 24, 55, 0.5);
        animation: none;
    }
    
    .chat-bubble-icon {
        color: white;
        font-size: 28px;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    /* Enhanced Chat Messages */
    .user-message-enhanced {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        padding: 16px 20px;
        border-radius: 20px 20px 8px 20px;
        margin: 12px 0;
        margin-left: 60px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
        position: relative;
    }
    
    .user-message-enhanced::before {
        content: '🙋';
        position: absolute;
        left: -45px;
        top: 50%;
        transform: translateY(-50%);
        width: 35px;
        height: 35px;
        background: linear-gradient(135deg, #6c757d, #495057);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
    }
    
    .ai-message-enhanced {
        background: linear-gradient(135deg, #E31837, #ff4757);
        color: white;
        padding: 16px 20px;
        border-radius: 20px 20px 20px 8px;
        margin: 12px 0;
        margin-right: 60px;
        box-shadow: 0 4px 15px rgba(227, 24, 55, 0.3);
        position: relative;
    }
    
    .ai-message-enhanced::after {
        content: '🤖';
        position: absolute;
        right: -45px;
        top: 50%;
        transform: translateY(-50%);
        width: 35px;
        height: 35px;
        background: linear-gradient(135deg, #E31837, #ff4757);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(227, 24, 55, 0.3);
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #E31837, #ff4757);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(227, 24, 55, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(227, 24, 55, 0.3);
        background: linear-gradient(135deg, #d12a47, #ff5757);
    }
    
    /* Quick Action Buttons */
    .quick-action-btn {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 2px solid #E31837;
        color: #E31837;
        padding: 12px 20px;
        border-radius: 25px;
        font-weight: 500;
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
        box-shadow: 0 2px 10px rgba(227, 24, 55, 0.1);
    }
    
    .quick-action-btn:hover {
        background: linear-gradient(135deg, #E31837, #ff4757);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(227, 24, 55, 0.3);
    }
    
    /* Status Indicators */
    .status-good {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #ffc107, #fd7e14);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-danger {
        background: linear-gradient(135deg, #dc3545, #e74c3c);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        display: inline-block;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #E31837, #ff4757);
        border-radius: 10px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 12px 20px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #E31837, #ff4757);
        color: white;
        border-color: #E31837;
    }
    
    /* File Uploader */
    .stFileUploader > div > div {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border: 2px dashed #E31837;
        border-radius: 16px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div > div:hover {
        border-color: #ff4757;
        background: linear-gradient(135deg, #fff5f5, #ffe8e8);
    }
    
    /* Expandable Sections */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa, #e9ecef);
        border-radius: 12px;
        border: 1px solid #dee2e6;
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 12px;
        border: 2px solid #dee2e6;
    }
    
    /* Text Input */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 12px;
        border: 2px solid #dee2e6;
        padding: 12px 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #E31837;
        box-shadow: 0 0 0 3px rgba(227, 24, 55, 0.1);
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Additional Sidebar Classes */
    .css-17eq0hr {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        min-width: 300px !important;
        width: 300px !important;
    }
    
    /* Streamlit sidebar container */
    .css-1544g2n {
        min-width: 300px !important;
        width: 300px !important;
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: #E31837 !important;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #d4edda, #c3e6cb);
        border: 1px solid #28a745;
        border-radius: 12px;
    }
    
    .stError {
        background: linear-gradient(135deg, #f8d7da, #f5c6cb);
        border: 1px solid #dc3545;
        border-radius: 12px;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #fff3cd, #ffeaa7);
        border: 1px solid #ffc107;
        border-radius: 12px;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #d1ecf1, #bee5eb);
        border: 1px solid #17a2b8;
        border-radius: 12px;
    }
</style>

<script>
// Force sidebar to stay expanded
document.addEventListener('DOMContentLoaded', function() {
    // Function to keep sidebar expanded
    function keepSidebarExpanded() {
        // Target sidebar using data-testid attribute
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        
        // Target all possible sidebar containers with various class names
        const sidebarSelectors = [
            '.css-1d391kg', '.css-1lcbmhc', '.css-1cypcdb', '.css-17eq0hr', 
            '.css-1544g2n', '.css-1fcdlhc', '.css-1vq4p4l', '.css-6qob1r', 
            '.css-79elbk', '.css-1oe6oti'
        ];
        
        // Apply styles to main sidebar container
        if (sidebar) {
            sidebar.style.display = 'block';
            sidebar.style.transform = 'none';
            sidebar.style.minWidth = '300px';
            sidebar.style.width = '300px';
            sidebar.style.position = 'relative';
            sidebar.style.visibility = 'visible';
            sidebar.style.opacity = '1';
            sidebar.style.transition = 'none';
        }
        
        // Apply styles to all possible sidebar containers
        sidebarSelectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el) {
                    el.style.display = 'block';
                    el.style.transform = 'none';
                    el.style.minWidth = '300px';
                    el.style.width = '300px';
                    el.style.position = 'relative';
                    el.style.visibility = 'visible';
                    el.style.opacity = '1';
                    el.style.transition = 'none';
                }
            });
        });
        
        // Hide all collapse buttons
        const collapseButtons = document.querySelectorAll('[data-testid="collapsedControl"], .css-1rs6os, .css-hied5v');
        collapseButtons.forEach(btn => {
            if (btn) btn.style.display = 'none';
        });
        
        // Force cookie setting for sidebar state
        try {
            // Try to set a cookie to remember sidebar state
            document.cookie = 'streamlit_sidebarState=expanded; path=/; max-age=31536000; SameSite=Lax';
            
            // Also try localStorage as a backup
            localStorage.setItem('streamlit_sidebarState', 'expanded');
        } catch (e) {
            console.log('Unable to set sidebar state in storage', e);
        }
    }
    
    // Run immediately
    keepSidebarExpanded();
    
    // Run after a short delay to catch any late DOM changes
    setTimeout(keepSidebarExpanded, 100);
    setTimeout(keepSidebarExpanded, 500);
    setTimeout(keepSidebarExpanded, 1000);
    
    // Use MutationObserver to watch for changes
    const observer = new MutationObserver(keepSidebarExpanded);
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        attributeFilter: ['style', 'class', 'data-testid']
    });
    
    // Also run on window resize and visibility change
    window.addEventListener('resize', keepSidebarExpanded);
    document.addEventListener('visibilitychange', keepSidebarExpanded);
});
</script>
""", unsafe_allow_html=True)



def main():
    # Enhanced Header with Logo and Branding
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <h1 class="main-header">💄 L'Oréal YouTube Comment Quality Analysis</h1>
        <p style="font-size: 1.2rem; color: #6c757d; margin-top: -1rem; font-weight: 300;">
            AI-Powered Beauty Content Analytics Platform
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: 1rem;">
            <span style="background: linear-gradient(135deg, #E31837, #ff4757); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                🤖 AI Assistant
            </span>
            <span style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                📊 Real-time Analytics
            </span>
            <span style="background: linear-gradient(135deg, #17a2b8, #6f42c1); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                🎯 Smart Insights
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced Sidebar
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #E31837, #ff4757); border-radius: 16px; margin-bottom: 2rem; color: white;">
        <h2 style="margin: 0; font-size: 1.5rem; font-weight: 600;">📊 Analytics Dashboard</h2>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">Powered by Advanced Analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    
    # Enhanced Navigation
    st.sidebar.markdown("### 🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📤 Upload Data", "🔍 Analysis Results", "📈 Visualizations", "🤖 AI Assistant", "📋 Data Export"],
        help="Navigate through different sections of the analysis platform"
    )
    

    
    # Main page routing
    if page == "📤 Upload Data":
        upload_page()
    elif page == "🔍 Analysis Results":
        analysis_page()
    elif page == "📈 Visualizations":
        visualization_page()
    elif page == "🤖 AI Assistant":
        ai_assistant_page()
    elif page == "📋 Data Export":
        export_page()
    


def check_system_resources():
    """Check system resources for large dataset processing"""
    try:
        memory = psutil.virtual_memory()
        return {
            'total_memory_gb': memory.total / (1024**3),
            'available_memory_gb': memory.available / (1024**3),
            'memory_percent': memory.percent,
            'cpu_count': psutil.cpu_count()
        }
    except:
        return None

def upload_page():
    # Enhanced Upload Page Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📤</div>
        <h1 style="margin: 0; color: #E31837; font-size: 2.5rem;">Upload Your Data</h1>
        <p style="margin: 1rem 0 0 0; color: #6c757d; font-size: 1.2rem;">Start your AI-powered comment analysis journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload mode selection
    upload_mode = st.radio(
        "Choose upload mode:",
        ["Single Dataset", "Multiple Datasets (Batch)"],
        horizontal=True
    )
    
    # Enhanced System Resources Display
    resources = check_system_resources()
    if resources:
        with st.expander("💻 System Resources & Performance", expanded=False):
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f8f9fa, #ffffff); padding: 1rem; border-radius: 12px; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #E31837;">System Performance Monitor</h4>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                memory_color = "#28a745" if resources['available_memory_gb'] > 4 else "#ffc107" if resources['available_memory_gb'] > 2 else "#dc3545"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffffff, #f8f9fa); padding: 1rem; border-radius: 12px; text-align: center; border-left: 4px solid {memory_color};">
                    <div style="font-size: 1.5rem; font-weight: 600; color: {memory_color};">{resources['available_memory_gb']:.1f} GB</div>
                    <div style="font-size: 0.9rem; color: #6c757d;">Available Memory</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffffff, #f8f9fa); padding: 1rem; border-radius: 12px; text-align: center; border-left: 4px solid #17a2b8;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: #17a2b8;">{resources['cpu_count']}</div>
                    <div style="font-size: 0.9rem; color: #6c757d;">CPU Cores</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                usage_color = "#28a745" if resources['memory_percent'] < 70 else "#ffc107" if resources['memory_percent'] < 85 else "#dc3545"
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #ffffff, #f8f9fa); padding: 1rem; border-radius: 12px; text-align: center; border-left: 4px solid {usage_color};">
                    <div style="font-size: 1.5rem; font-weight: 600; color: {usage_color};">{resources['memory_percent']:.0f}%</div>
                    <div style="font-size: 0.9rem; color: #6c757d;">Memory Usage</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Enhanced warnings
            if resources['available_memory_gb'] < 2:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f8d7da, #f5c6cb); padding: 1rem; border-radius: 12px; border-left: 4px solid #dc3545; margin-top: 1rem;">
                    <strong>⚠️ Low Memory Warning:</strong> Large datasets may fail to process. Consider using a more powerful system or enable sampling.
                </div>
                """, unsafe_allow_html=True)
            elif resources['available_memory_gb'] < 4:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #fff3cd, #ffeaa7); padding: 1rem; border-radius: 12px; border-left: 4px solid #ffc107; margin-top: 1rem;">
                    <strong>💡 Performance Tip:</strong> Limited memory detected. Consider using sampling for datasets > 50k comments for optimal performance.
                </div>
                """, unsafe_allow_html=True)
    
    if upload_mode == "Single Dataset":
        upload_single_dataset()
    else:
        upload_multiple_datasets()

def upload_single_dataset():
    """Handle single dataset upload"""
    # Instructions
    with st.expander("📋 Data Format Requirements", expanded=True):
        st.markdown("""
        **Required CSV Files:**
        
        **1. Comments File** - Must contain:
        - `videoId`: Video identifier
        - `textOriginal`: Comment text
        - `likeCount`: Number of likes (optional)
        - `replyCount`: Number of replies (optional)
        - `publishedAt`: Timestamp (optional)
        
        **2. Videos File** - Must contain:
        - `videoId`: Video identifier (must match comments)
        - `title`: Video title
        - `description`: Video description (optional)
        - `viewCount`: View count (optional)
        - `likeCount`: Video likes (optional)
        - `commentCount`: Total comments (optional)
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Comments Data")
        comments_file = st.file_uploader(
            "Upload comments CSV file",
            type=['csv'],
            key="comments_upload",
            help="CSV file containing YouTube comments data"
        )
        
        if comments_file is not None:
            try:
                comments_df = pd.read_csv(comments_file)
                st.success(f"✅ Loaded {len(comments_df)} comments")
                
                # Show preview
                st.write("**Preview:**")
                st.dataframe(comments_df.head(), width='stretch')
                
                # Validate required columns
                required_cols = ['videoId', 'textOriginal']
                missing_cols = [col for col in required_cols if col not in comments_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {missing_cols}")
                else:
                    st.success("✅ All required columns present")
                    
                    # Show optional columns status
                    optional_cols = ['likeCount', 'replyCount', 'publishedAt']
                    available_optional = [col for col in optional_cols if col in comments_df.columns]
                    missing_optional = [col for col in optional_cols if col not in comments_df.columns]
                    
                    if available_optional:
                        st.info(f"📊 Optional columns found: {', '.join(available_optional)}")
                    if missing_optional:
                        st.info(f"ℹ️ Optional columns missing: {', '.join(missing_optional)} (analysis will continue without these)")
                    
            except Exception as e:
                st.error(f"❌ Error reading comments file: {e}")
    
    with col2:
        st.subheader("🎥 Videos Data")
        videos_file = st.file_uploader(
            "Upload videos CSV file",
            type=['csv'],
            key="videos_upload",
            help="CSV file containing YouTube videos metadata"
        )
        
        if videos_file is not None:
            try:
                videos_df = pd.read_csv(videos_file)
                st.success(f"✅ Loaded {len(videos_df)} videos")
                
                # Show preview
                st.write("**Preview:**")
                st.dataframe(videos_df.head(), width='stretch')
                
                # Validate required columns
                required_cols = ['videoId', 'title']
                missing_cols = [col for col in required_cols if col not in videos_df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {missing_cols}")
                else:
                    st.success("✅ All required columns present")
                    
            except Exception as e:
                st.error(f"❌ Error reading videos file: {e}")
    
    # Analysis button
    if comments_file is not None and videos_file is not None:
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Analysis", type="primary", width='stretch'):
                run_analysis(comments_df, videos_df)

def upload_multiple_datasets():
    """Handle multiple dataset upload and batch processing"""
    st.subheader("📊 Batch Processing Mode")
    
    with st.expander("📋 Batch Processing Instructions", expanded=True):
        st.markdown("""
        **Upload Multiple Files:**
        1. Upload multiple comment and video CSV files
        2. Files will be automatically matched by name similarity
        3. All datasets will be processed in sequence
        4. Results will be combined into a comprehensive report
        
        **File Naming Convention:**
        - Comment files: Include 'comment' in filename (e.g., `dataset1_comments.csv`)
        - Video files: Include 'video' in filename (e.g., `dataset1_videos.csv`)
        - Or ensure comment files have `textOriginal` column for auto-detection
        """)
    
    # Multiple file upload
    st.subheader("📁 Upload Multiple Files")
    
    uploaded_files = st.file_uploader(
        "Upload multiple CSV files (comments and videos)",
        type=['csv'],
        accept_multiple_files=True,
        help="Upload all your CSV files at once. The system will automatically detect and match comment/video pairs."
    )
    
    if uploaded_files:
        st.success(f"✅ Uploaded {len(uploaded_files)} files")
        
        # Categorize files
        comment_files = []
        video_files = []
        unknown_files = []
        
        for file in uploaded_files:
            filename = file.name.lower()
            
            # Try to categorize by filename
            if 'comment' in filename:
                comment_files.append(file)
            elif 'video' in filename:
                video_files.append(file)
            else:
                # Try to detect by content
                try:
                    df_sample = pd.read_csv(file, nrows=1)
                    if 'textOriginal' in df_sample.columns:
                        comment_files.append(file)
                    elif 'title' in df_sample.columns:
                        video_files.append(file)
                    else:
                        unknown_files.append(file)
                    file.seek(0)  # Reset file pointer
                except:
                    unknown_files.append(file)
        
        # Show categorization results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Comment Files", len(comment_files))
            if comment_files:
                with st.expander("Comment Files"):
                    for f in comment_files:
                        st.write(f"📝 {f.name}")
        
        with col2:
            st.metric("Video Files", len(video_files))
            if video_files:
                with st.expander("Video Files"):
                    for f in video_files:
                        st.write(f"🎥 {f.name}")
        
        with col3:
            st.metric("Unknown Files", len(unknown_files))
            if unknown_files:
                with st.expander("Unknown Files"):
                    for f in unknown_files:
                        st.write(f"❓ {f.name}")
                st.warning("Unknown files will be skipped. Please check file format.")
        
        # Batch processing options
        if comment_files:
            st.markdown("---")
            st.subheader("⚙️ Batch Processing Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                combine_results = st.checkbox("Combine all results into single report", value=True)
                generate_individual_reports = st.checkbox("Generate individual reports per dataset", value=True)
            
            with col2:
                use_sampling = st.checkbox("Use sampling for large datasets (>50k comments)", value=True)
                if use_sampling:
                    sample_size = st.slider("Sample size per dataset", 10000, 100000, 50000, 10000)
            
            # Start batch processing
            if st.button("🚀 Start Batch Processing", type="primary", width='stretch'):
                run_batch_analysis(
                    comment_files, 
                    video_files, 
                    combine_results, 
                    generate_individual_reports,
                    use_sampling,
                    sample_size if use_sampling else None
                )
        else:
            st.error("❌ No comment files detected. Please upload files with 'textOriginal' column.")

def run_analysis(comments_df, videos_df):
    """Run the complete analysis pipeline optimized for large datasets"""
    
    # Check dataset size and warn user
    total_comments = len(comments_df)
    if total_comments > 50000:
        st.warning(f"⚠️ Large dataset detected ({total_comments:,} comments). This may take several minutes to process.")
        
        # Offer sampling option for very large datasets
        if total_comments > 100000:
            col1, col2 = st.columns(2)
            with col1:
                use_sample = st.checkbox("Use sample for faster processing", value=True)
            with col2:
                if use_sample:
                    sample_size = st.slider("Sample size", 10000, 100000, 50000, 10000)
                    comments_df = comments_df.sample(n=sample_size, random_state=42)
                    st.info(f"Using sample of {len(comments_df):,} comments")
    
    with st.spinner("🔄 Processing data..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Data Processing
            status_text.text("📊 Processing and merging data...")
            progress_bar.progress(10)
            
            processor = DataProcessor()
            processor.comments_df = comments_df
            processor.videos_df = videos_df
            
            if not processor.merge_datasets():
                st.error("❌ Failed to merge datasets")
                return
            
            progress_bar.progress(20)
            
            if not processor.preprocess_data():
                st.error("❌ Failed to preprocess data")
                return
            
            progress_bar.progress(30)
            
            # Step 2: Comment Analysis
            status_text.text("🔍 Analyzing comments...")
            analyzer = CommentAnalyzer()
            
            # Optimize batch size based on dataset size
            if len(processor.merged_df) > 50000:
                batch_size = 1000  # Larger batches for big datasets
            elif len(processor.merged_df) > 10000:
                batch_size = 500
            else:
                batch_size = 250
            
            all_results = []
            total_batches = (len(processor.merged_df) - 1) // batch_size + 1
            
            status_text.text(f"🔍 Analyzing {len(processor.merged_df):,} comments in {total_batches} batches...")
            
            for i in range(0, len(processor.merged_df), batch_size):
                batch_num = (i // batch_size) + 1
                batch = processor.merged_df.iloc[i:i+batch_size]
                
                status_text.text(f"🔍 Processing batch {batch_num}/{total_batches} ({len(batch)} comments)...")
                
                batch_results = analyzer.analyze_comment_batch(batch)
                all_results.append(batch_results)
                
                # Update progress (30% to 85%)
                progress = 30 + (55 * batch_num / total_batches)
                progress_bar.progress(min(int(progress), 85))
            
            # Combine results
            status_text.text("🔗 Combining analysis results...")
            progress_bar.progress(85)
            
            analysis_df = pd.concat(all_results, ignore_index=True)
            
            # Add quality scores efficiently
            status_text.text("⭐ Calculating quality scores...")
            progress_bar.progress(90)
            
            quality_scores = []
            for _, row in analysis_df.iterrows():
                if row['comment_id'] < len(processor.merged_df):
                    original_row = processor.merged_df.iloc[row['comment_id']]
                    # Handle missing likeCount column
                    like_count = 0
                    if 'likeCount' in processor.merged_df.columns:
                        like_count = original_row.get('likeCount', 0)
                        # Convert to numeric if it's a string
                        try:
                            like_count = float(like_count) if like_count else 0
                        except (ValueError, TypeError):
                            like_count = 0
                    
                    quality_score = analyzer.generate_quality_score(
                        row['relevance'], 
                        row['vader_sentiment'], 
                        row['engagement_type'],
                        like_count
                    )
                    quality_scores.append(quality_score)
                else:
                    quality_scores.append(0)
            
            analysis_df['quality_score'] = quality_scores
            
            # Merge with original data
            final_df = processor.merged_df.merge(
                analysis_df, 
                left_index=True, 
                right_on='comment_id', 
                how='left'
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store results in session state
            st.session_state.processed_data = processor.merged_df
            st.session_state.analysis_results = final_df
            st.session_state.analysis_complete = True
            
            # Show success message with performance info
            processing_time = "Processing completed"
            st.success(f"🎉 Analysis completed successfully! {processing_time}")
            
            # Show comprehensive stats
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Comments", f"{len(final_df):,}")
            
            with col2:
                spam_rate = (final_df['is_spam'] == True).mean() * 100
                st.metric("Spam Rate", f"{spam_rate:.1f}%")
            
            with col3:
                avg_quality = final_df['quality_score'].mean()
                st.metric("Avg Quality", f"{avg_quality:.2f}/5")
            
            with col4:
                unique_videos = final_df['videoId'].nunique()
                st.metric("Unique Videos", f"{unique_videos:,}")
            
            with col5:
                genuine_rate = (final_df['relevance'] == 'genuine').mean() * 100
                st.metric("Genuine Rate", f"{genuine_rate:.1f}%")
            
            # Performance summary for large datasets
            if len(final_df) > 10000:
                st.info(f"📊 Large dataset processed: {len(final_df):,} comments analyzed successfully!")
            
            st.info("👈 Navigate to other pages using the sidebar to explore results!")
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.exception(e)
            
            # Provide helpful error messages for large datasets
            if "memory" in str(e).lower():
                st.error("💾 Memory error detected. Try using a smaller sample size or restart the app.")
            elif "timeout" in str(e).lower():
                st.error("⏱️ Processing timeout. Large datasets may take longer - please be patient.")

def run_batch_analysis(comment_files, video_files, combine_results, generate_individual_reports, use_sampling, sample_size):
    """Run batch analysis on multiple file pairs"""
    
    st.header("🔄 Batch Processing in Progress")
    
    # Auto-match files
    file_pairs = auto_match_files(comment_files, video_files)
    
    if not file_pairs:
        st.error("❌ No valid file pairs found for processing")
        return
    
    st.info(f"📊 Processing {len(file_pairs)} dataset pairs...")
    
    # Initialize results storage
    all_results = []
    individual_results = []
    
    # Progress tracking
    overall_progress = st.progress(0)
    status_container = st.container()
    
    for i, (comment_file, video_file, pair_name) in enumerate(file_pairs):
        with status_container:
            st.subheader(f"📊 Processing Dataset {i+1}/{len(file_pairs)}: {pair_name}")
            
            try:
                # Load data
                comments_df = pd.read_csv(comment_file)
                
                if video_file:
                    videos_df = pd.read_csv(video_file)
                else:
                    # Create dummy videos dataframe
                    unique_videos = comments_df['videoId'].unique()
                    videos_df = pd.DataFrame({
                        'videoId': unique_videos,
                        'title': [f'Video {j}' for j in range(len(unique_videos))],
                        'description': [''] * len(unique_videos)
                    })
                
                # Apply sampling if requested
                if use_sampling and len(comments_df) > sample_size:
                    st.info(f"📊 Sampling {sample_size:,} comments from {len(comments_df):,} total")
                    comments_df = comments_df.sample(n=sample_size, random_state=42)
                
                # Process this dataset
                processor = DataProcessor()
                processor.comments_df = comments_df
                processor.videos_df = videos_df
                
                if processor.merge_datasets() and processor.preprocess_data():
                    analyzer = CommentAnalyzer()
                    
                    # Analyze in batches
                    batch_size = 1000 if len(processor.merged_df) > 10000 else 500
                    batch_results = []
                    
                    for j in range(0, len(processor.merged_df), batch_size):
                        batch = processor.merged_df.iloc[j:j+batch_size]
                        result = analyzer.analyze_comment_batch(batch)
                        batch_results.append(result)
                    
                    # Combine batch results
                    analysis_df = pd.concat(batch_results, ignore_index=True)
                    
                    # Add quality scores
                    quality_scores = []
                    for _, row in analysis_df.iterrows():
                        if row['comment_id'] < len(processor.merged_df):
                            original_row = processor.merged_df.iloc[row['comment_id']]
                            like_count = 0
                            if 'likeCount' in processor.merged_df.columns:
                                like_count = original_row.get('likeCount', 0)
                                try:
                                    like_count = float(like_count) if like_count else 0
                                except (ValueError, TypeError):
                                    like_count = 0
                            
                            quality_score = analyzer.generate_quality_score(
                                row['relevance'], 
                                row['vader_sentiment'], 
                                row['engagement_type'],
                                like_count
                            )
                            quality_scores.append(quality_score)
                        else:
                            quality_scores.append(0)
                    
                    analysis_df['quality_score'] = quality_scores
                    
                    # Merge with original data
                    final_df = processor.merged_df.merge(
                        analysis_df, 
                        left_index=True, 
                        right_on='comment_id', 
                        how='left'
                    )
                    
                    # Add dataset identifier
                    final_df['dataset_name'] = pair_name
                    
                    # Store results
                    if combine_results:
                        all_results.append(final_df)
                    
                    if generate_individual_reports:
                        individual_results.append({
                            'name': pair_name,
                            'data': final_df,
                            'total_comments': len(final_df),
                            'spam_rate': (final_df['is_spam'] == True).mean() * 100,
                            'avg_quality': final_df['quality_score'].mean(),
                            'positive_sentiment': (final_df['vader_sentiment'] == 'positive').mean() * 100
                        })
                    
                    st.success(f"✅ {pair_name} processed successfully! ({len(final_df):,} comments)")
                    
                else:
                    st.error(f"❌ Failed to process {pair_name}")
                    
            except Exception as e:
                st.error(f"❌ Error processing {pair_name}: {e}")
            
            # Update progress
            overall_progress.progress((i + 1) / len(file_pairs))
    
    # Process combined results
    if combine_results and all_results:
        st.header("📊 Combined Results")
        
        combined_df = pd.concat(all_results, ignore_index=True)
        
        # Store in session state
        st.session_state.processed_data = combined_df
        st.session_state.analysis_results = combined_df
        st.session_state.analysis_complete = True
        
        # Show combined metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Comments", f"{len(combined_df):,}")
        
        with col2:
            spam_rate = (combined_df['is_spam'] == True).mean() * 100
            st.metric("Overall Spam Rate", f"{spam_rate:.1f}%")
        
        with col3:
            avg_quality = combined_df['quality_score'].mean()
            st.metric("Avg Quality Score", f"{avg_quality:.2f}/5")
        
        with col4:
            positive_rate = (combined_df['vader_sentiment'] == 'positive').mean() * 100
            st.metric("Positive Sentiment", f"{positive_rate:.1f}%")
        
        with col5:
            datasets_count = combined_df['dataset_name'].nunique()
            st.metric("Datasets Processed", f"{datasets_count}")
        
        st.success("🎉 Batch processing completed! Navigate to other pages to explore results.")
    
    # Show individual results summary
    if generate_individual_reports and individual_results:
        st.header("📋 Individual Dataset Summary")
        
        summary_data = []
        for result in individual_results:
            summary_data.append({
                'Dataset': result['name'],
                'Comments': f"{result['total_comments']:,}",
                'Spam Rate': f"{result['spam_rate']:.1f}%",
                'Avg Quality': f"{result['avg_quality']:.2f}/5",
                'Positive %': f"{result['positive_sentiment']:.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, width='stretch')

def auto_match_files(comment_files, video_files):
    """Automatically match comment and video files"""
    pairs = []
    used_video_files = set()
    
    for i, comment_file in enumerate(comment_files):
        comment_name = comment_file.name.lower()
        best_match = None
        best_score = 0
        
        # Try to find matching video file
        for video_file in video_files:
            if video_file.name in used_video_files:
                continue
                
            video_name = video_file.name.lower()
            
            # Calculate similarity score
            comment_base = comment_name.replace('comment', '').replace('.csv', '')
            video_base = video_name.replace('video', '').replace('.csv', '')
            
            # Simple similarity scoring
            score = 0
            if comment_base == video_base:
                score = 100
            elif comment_base in video_base or video_base in comment_base:
                score = 80
            elif any(part in video_base for part in comment_base.split('_') if len(part) > 2):
                score = 60
            
            if score > best_score:
                best_score = score
                best_match = video_file
        
        if best_match:
            used_video_files.add(best_match.name)
            pair_name = f"dataset_{i+1:02d}"
            pairs.append((comment_file, best_match, pair_name))
        else:
            # Use without video file
            pair_name = f"dataset_{i+1:02d}"
            pairs.append((comment_file, None, pair_name))
    
    return pairs

def analysis_page():
    st.header("🔍 Analysis Results")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    # Overview metrics
    st.subheader("📊 Overview Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_comments = len(df)
        st.metric("Total Comments", f"{total_comments:,}")
    
    with col2:
        spam_rate = (df['is_spam'] == True).mean() * 100
        st.metric("Spam Rate", f"{spam_rate:.1f}%", delta=f"{spam_rate-15:.1f}%" if spam_rate < 15 else None)
    
    with col3:
        avg_quality = df['quality_score'].mean()
        st.metric("Avg Quality Score", f"{avg_quality:.2f}/5")
    
    with col4:
        positive_rate = (df['vader_sentiment'] == 'positive').mean() * 100
        st.metric("Positive Sentiment", f"{positive_rate:.1f}%")
    
    with col5:
        unique_videos = df['videoId'].nunique()
        st.metric("Unique Videos", f"{unique_videos:,}")
    
    # Detailed breakdown
    st.subheader("📈 Detailed Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Relevance Distribution**")
        relevance_counts = df['relevance'].value_counts()
        fig_relevance = px.pie(
            values=relevance_counts.values,
            names=relevance_counts.index,
            title="Comment Relevance",
            color_discrete_map={
                'genuine': '#2E8B57',
                'general': '#4682B4',
                'spam': '#DC143C'
            }
        )
        st.plotly_chart(fig_relevance, width='stretch')
    
    with col2:
        st.write("**Sentiment Distribution**")
        sentiment_counts = df['vader_sentiment'].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Comment Sentiment",
            color_discrete_map={
                'positive': '#32CD32',
                'neutral': '#FFD700',
                'negative': '#FF6347'
            }
        )
        st.plotly_chart(fig_sentiment, width='stretch')
    
    # Enhanced Comment Filtering Section
    st.markdown("---")
    st.markdown("## 🔍 Advanced Comment Filtering & Analysis")
    
    # Create tabs for different filtering approaches
    filter_tab1, filter_tab2, filter_tab3 = st.tabs([
        "🎯 Category Filters", 
        "📊 Advanced Search", 
        "🏷️ Predefined Categories"
    ])
    
    with filter_tab1:
        st.markdown("### 🎯 Filter Comments by Categories")
        
        # Multi-column filter layout
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            relevance_filter = st.multiselect(
                "Relevance Type:",
                options=list(df['relevance'].unique()),
                default=list(df['relevance'].unique()),
                help="Filter by comment relevance to video content"
            )
        
        with col2:
            sentiment_filter = st.multiselect(
                "Sentiment:",
                options=list(df['vader_sentiment'].unique()),
                default=list(df['vader_sentiment'].unique()),
                help="Filter by emotional sentiment of comments"
            )
        
        with col3:
            engagement_filter = st.multiselect(
                "Engagement Type:",
                options=list(df['engagement_type'].unique()),
                default=list(df['engagement_type'].unique()),
                help="Filter by type of audience engagement"
            )
        
        with col4:
            # Beauty category filter
            if 'beauty_category' in df.columns:
                category_filter = st.multiselect(
                    "🏷️ Beauty Category:",
                    options=sorted(list(df['beauty_category'].unique())),
                    default=sorted(list(df['beauty_category'].unique())),
                    help="Filter by beauty product category"
                )
            else:
                category_filter = None
        
        with col5:
            spam_filter = st.selectbox(
                "Spam Status:",
                options=["All", "Non-Spam Only", "Spam Only"],
                help="Filter by spam detection results"
            )
        
        # Quality and date range filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quality_range = st.slider(
                "Quality Score Range:",
                min_value=0.0,
                max_value=5.0,
                value=(0.0, 5.0),
                step=0.1,
                help="Filter by comment quality score"
            )
        
        with col2:
            if 'likeCount' in df.columns:
                like_range = st.slider(
                    "Like Count Range:",
                    min_value=int(df['likeCount'].min()),
                    max_value=int(df['likeCount'].quantile(0.95)),  # Exclude extreme outliers
                    value=(int(df['likeCount'].min()), int(df['likeCount'].quantile(0.95))),
                    help="Filter by number of likes received"
                )
            else:
                like_range = None
        
        with col3:
            if 'publishedAt' in df.columns:
                try:
                    df['date'] = pd.to_datetime(df['publishedAt']).dt.date
                    min_date = df['date'].min()
                    max_date = df['date'].max()
                    
                    date_range = st.date_input(
                        "Date Range:",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        help="Filter by comment publication date"
                    )
                except:
                    date_range = None
            else:
                date_range = None
    
    with filter_tab2:
        st.markdown("### 📊 Advanced Search & Text Filtering")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Text search
            search_text = st.text_input(
                "Search in Comments:",
                placeholder="Enter keywords to search for...",
                help="Search for specific words or phrases in comments"
            )
            
            # Text length filter
            if 'textOriginal_cleaned' in df.columns:
                text_lengths = df['textOriginal_cleaned'].str.len()
                length_range = st.slider(
                    "Comment Length (characters):",
                    min_value=int(text_lengths.min()),
                    max_value=int(text_lengths.quantile(0.95)),
                    value=(int(text_lengths.min()), int(text_lengths.quantile(0.95))),
                    help="Filter by comment length"
                )
            else:
                length_range = None
        
        with col2:
            # Video filter (if available)
            if 'title' in df.columns:
                video_filter = st.multiselect(
                    "Filter by Video:",
                    options=list(df['title'].unique()),
                    default=[],
                    help="Select specific videos to analyze"
                )
            else:
                video_filter = []
            
            # Sort options
            sort_by = st.selectbox(
                "Sort Results By:",
                options=[
                    "Quality Score (High to Low)",
                    "Quality Score (Low to High)",
                    "Like Count (High to Low)",
                    "Date (Newest First)",
                    "Date (Oldest First)",
                    "Comment Length (Long to Short)"
                ],
                help="Choose how to sort the filtered results"
            )
    
    with filter_tab3:
        st.markdown("### 🏷️ Predefined Comment Categories")
        
        # Quick filter buttons for common categories
        st.markdown("**Quick Filters:**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🌟 High Quality Comments", width='stretch'):
                st.session_state.quick_filter = "high_quality"
        
        with col2:
            if st.button("❓ Questions Only", width='stretch'):
                st.session_state.quick_filter = "questions"
        
        with col3:
            if st.button("💖 Positive Feedback", width='stretch'):
                st.session_state.quick_filter = "positive"
        
        with col4:
            if st.button("🚨 Spam & Low Quality", width='stretch'):
                st.session_state.quick_filter = "spam_low"
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🎓 Tutorial Requests", width='stretch'):
                st.session_state.quick_filter = "tutorial_requests"
        
        with col2:
            if st.button("🛍️ Product Inquiries", width='stretch'):
                st.session_state.quick_filter = "product_inquiries"
        
        with col3:
            if st.button("👥 Personal Stories", width='stretch'):
                st.session_state.quick_filter = "personal_stories"
        
        with col4:
            if st.button("🔄 Reset Filters", width='stretch'):
                st.session_state.quick_filter = "reset"
    
    # Apply all filters
    filtered_df = df.copy()
    
    # Apply quick filters if selected
    if 'quick_filter' in st.session_state:
        if st.session_state.quick_filter == "high_quality":
            filtered_df = filtered_df[filtered_df['quality_score'] >= 4.0]
            st.info("🌟 Showing high quality comments (score ≥ 4.0)")
        elif st.session_state.quick_filter == "questions":
            filtered_df = filtered_df[filtered_df['engagement_type'] == 'question']
            st.info("❓ Showing question-type comments only")
        elif st.session_state.quick_filter == "positive":
            filtered_df = filtered_df[
                (filtered_df['vader_sentiment'] == 'positive') & 
                (filtered_df['quality_score'] >= 3.0)
            ]
            st.info("💖 Showing positive feedback comments")
        elif st.session_state.quick_filter == "spam_low":
            filtered_df = filtered_df[
                (filtered_df['is_spam'] == True) | 
                (filtered_df['quality_score'] < 2.0)
            ]
            st.info("🚨 Showing spam and low quality comments")
        elif st.session_state.quick_filter == "tutorial_requests":
            filtered_df = filtered_df[filtered_df['engagement_type'] == 'technique_request']
            st.info("🎓 Showing tutorial and technique requests")
        elif st.session_state.quick_filter == "product_inquiries":
            filtered_df = filtered_df[filtered_df['engagement_type'] == 'product_inquiry']
            st.info("🛍️ Showing product-related inquiries")
        elif st.session_state.quick_filter == "personal_stories":
            filtered_df = filtered_df[filtered_df['engagement_type'] == 'personal_story']
            st.info("👥 Showing personal stories and experiences")
        elif st.session_state.quick_filter == "reset":
            st.session_state.quick_filter = None
            st.success("🔄 All filters reset")
    
    # Apply manual filters
    if relevance_filter:
        filtered_df = filtered_df[filtered_df['relevance'].isin(relevance_filter)]
    
    if sentiment_filter:
        filtered_df = filtered_df[filtered_df['vader_sentiment'].isin(sentiment_filter)]
    
    if engagement_filter:
        filtered_df = filtered_df[filtered_df['engagement_type'].isin(engagement_filter)]
    
    # Apply beauty category filter
    if category_filter and 'beauty_category' in df.columns:
        filtered_df = filtered_df[filtered_df['beauty_category'].isin(category_filter)]
    
    # Apply spam filter
    if spam_filter == "Non-Spam Only":
        filtered_df = filtered_df[filtered_df['is_spam'] == False]
    elif spam_filter == "Spam Only":
        filtered_df = filtered_df[filtered_df['is_spam'] == True]
    
    # Apply quality range
    filtered_df = filtered_df[
        (filtered_df['quality_score'] >= quality_range[0]) & 
        (filtered_df['quality_score'] <= quality_range[1])
    ]
    
    # Apply like count filter
    if like_range and 'likeCount' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['likeCount'] >= like_range[0]) & 
            (filtered_df['likeCount'] <= like_range[1])
        ]
    
    # Apply date filter
    if date_range and 'date' in df.columns:
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['date'] >= date_range[0]) & 
                (filtered_df['date'] <= date_range[1])
            ]
    
    # Apply text search
    if search_text and 'textOriginal_cleaned' in df.columns:
        filtered_df = filtered_df[
            filtered_df['textOriginal_cleaned'].str.contains(
                search_text, case=False, na=False
            )
        ]
    
    # Apply text length filter
    if length_range and 'textOriginal_cleaned' in df.columns:
        text_lengths = filtered_df['textOriginal_cleaned'].str.len()
        filtered_df = filtered_df[
            (text_lengths >= length_range[0]) & 
            (text_lengths <= length_range[1])
        ]
    
    # Apply video filter
    if video_filter and 'title' in df.columns:
        filtered_df = filtered_df[filtered_df['title'].isin(video_filter)]
    
    # Apply sorting
    if sort_by == "Quality Score (High to Low)":
        filtered_df = filtered_df.sort_values('quality_score', ascending=False)
    elif sort_by == "Quality Score (Low to High)":
        filtered_df = filtered_df.sort_values('quality_score', ascending=True)
    elif sort_by == "Like Count (High to Low)" and 'likeCount' in df.columns:
        filtered_df = filtered_df.sort_values('likeCount', ascending=False)
    elif sort_by == "Date (Newest First)" and 'publishedAt' in df.columns:
        filtered_df = filtered_df.sort_values('publishedAt', ascending=False)
    elif sort_by == "Date (Oldest First)" and 'publishedAt' in df.columns:
        filtered_df = filtered_df.sort_values('publishedAt', ascending=True)
    elif sort_by == "Comment Length (Long to Short)" and 'textOriginal_cleaned' in df.columns:
        filtered_df = filtered_df.sort_values(
            filtered_df['textOriginal_cleaned'].str.len(), ascending=False
        )
    
    # Display filtered results
    st.markdown("---")
    st.markdown("## 📋 Filtered Comments Results")
    
    # Results summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Filtered Comments", f"{len(filtered_df):,}")
    
    with col2:
        if len(df) > 0:
            filter_percentage = (len(filtered_df) / len(df)) * 100
            st.metric("% of Total", f"{filter_percentage:.1f}%")
    
    with col3:
        if len(filtered_df) > 0:
            avg_quality_filtered = filtered_df['quality_score'].mean()
            st.metric("Avg Quality (Filtered)", f"{avg_quality_filtered:.2f}")
    
    with col4:
        if len(filtered_df) > 0:
            positive_rate_filtered = (filtered_df['vader_sentiment'] == 'positive').mean() * 100
            st.metric("Positive % (Filtered)", f"{positive_rate_filtered:.1f}%")
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(filtered_df) > 0:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                "📥 Download Filtered Data (CSV)",
                csv_data,
                file_name=f"filtered_comments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        if st.button("📊 Analyze Filtered Data", use_container_width=True):
            if len(filtered_df) > 0:
                # Store filtered data for analysis
                st.session_state.filtered_analysis_data = filtered_df
                st.success("Filtered data ready for detailed analysis!")
            else:
                st.warning("No data to analyze with current filters")
    
    with col3:
        if st.button("🔄 Reset All Filters", use_container_width=True):
            st.rerun()
    
    # Display the filtered comments table
    if len(filtered_df) > 0:
        # Select display columns
        display_columns = []
        available_cols = filtered_df.columns.tolist()
        
        # Always include these if available
        priority_cols = [
            'textOriginal_cleaned', 'relevance', 'vader_sentiment', 
            'engagement_type', 'quality_score'
        ]
        
        for col in priority_cols:
            if col in available_cols:
                display_columns.append(col)
        
        # Add optional columns if available
        optional_cols = ['likeCount', 'publishedAt', 'title']
        for col in optional_cols:
            if col in available_cols:
                display_columns.append(col)
        
        # Limit to first 500 rows for performance
        display_df = filtered_df[display_columns].head(500)
        
        # Style the dataframe
        def style_quality_score(val):
            if val >= 4:
                return 'background-color: #d4edda'  # Green
            elif val >= 3:
                return 'background-color: #fff3cd'  # Yellow
            elif val >= 2:
                return 'background-color: #f8d7da'  # Light red
            else:
                return 'background-color: #f5c6cb'  # Red
        
        def style_sentiment(val):
            if val == 'positive':
                return 'background-color: #d4edda; color: #155724'
            elif val == 'negative':
                return 'background-color: #f8d7da; color: #721c24'
            else:
                return 'background-color: #fff3cd; color: #856404'
        
        # Apply styling if quality_score column exists
        if 'quality_score' in display_df.columns:
            styled_df = display_df.style.applymap(
                style_quality_score, subset=['quality_score']
            )
            if 'vader_sentiment' in display_df.columns:
                styled_df = styled_df.applymap(
                    style_sentiment, subset=['vader_sentiment']
                )
        else:
            styled_df = display_df
        
        st.dataframe(styled_df, use_container_width=True, height=600)
        
        if len(filtered_df) > 500:
            st.info(f"Showing first 500 of {len(filtered_df):,} filtered comments. Use export to get all data.")
    
    else:
        st.warning("No comments match the current filter criteria. Try adjusting your filters.")
    
    # Category insights
    if len(filtered_df) > 0:
        st.markdown("---")
        st.markdown("### 📈 Filtered Data Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top engagement types in filtered data
            engagement_dist = filtered_df['engagement_type'].value_counts()
            fig_filtered_engagement = px.bar(
                x=engagement_dist.values,
                y=engagement_dist.index,
                orientation='h',
                title="Engagement Types in Filtered Data",
                labels={'x': 'Count', 'y': 'Engagement Type'}
            )
            st.plotly_chart(fig_filtered_engagement, use_container_width=True)
        
        with col2:
            # Quality distribution in filtered data
            fig_filtered_quality = px.histogram(
                filtered_df,
                x='quality_score',
                title="Quality Score Distribution (Filtered)",
                nbins=20
            )
            st.plotly_chart(fig_filtered_quality, use_container_width=True)

def visualization_page():
    # Enhanced Visualization Page Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📈</div>
        <h1 style="margin: 0; color: #E31837; font-size: 2.5rem;">Advanced Data Visualizations</h1>
        <p style="margin: 1rem 0 0 0; color: #6c757d; font-size: 1.2rem;">Comprehensive insights through interactive charts and analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    # Sidebar filters for interactive analysis
    with st.sidebar:
        st.markdown("### 🔍 Visualization Filters")
        
        # Sentiment filter
        sentiment_options = ['All'] + list(df['vader_sentiment'].unique())
        selected_sentiment = st.selectbox("Filter by Sentiment", sentiment_options)
        
        # Engagement type filter
        engagement_options = ['All'] + list(df['engagement_type'].unique())
        selected_engagement = st.selectbox("Filter by Engagement Type", engagement_options)
        
        # Beauty category filter
        if 'beauty_category' in df.columns:
            category_options = ['All'] + sorted(list(df['beauty_category'].unique()))
            selected_category = st.selectbox("🏷️ Filter by Beauty Category", category_options)
        else:
            selected_category = 'All'
        
        # Quality score filter
        min_quality = float(df['quality_score'].min())
        max_quality = float(df['quality_score'].max())
        quality_range = st.slider("Quality Score Range", min_quality, max_quality, (min_quality, max_quality))
        
        # Confidence filter for categories
        if 'category_confidence' in df.columns:
            min_confidence = st.slider("Category Confidence Threshold", 0.0, 1.0, 0.0, 0.1)
        else:
            min_confidence = 0.0
        
        # Apply filters
        filtered_df = df.copy()
        if selected_sentiment != 'All':
            filtered_df = filtered_df[filtered_df['vader_sentiment'] == selected_sentiment]
        if selected_engagement != 'All':
            filtered_df = filtered_df[filtered_df['engagement_type'] == selected_engagement]
        if selected_category != 'All' and 'beauty_category' in df.columns:
            filtered_df = filtered_df[filtered_df['beauty_category'] == selected_category]
        if 'category_confidence' in df.columns:
            filtered_df = filtered_df[filtered_df['category_confidence'] >= min_confidence]
        filtered_df = filtered_df[
            (filtered_df['quality_score'] >= quality_range[0]) & 
            (filtered_df['quality_score'] <= quality_range[1])
        ]
        
        st.info(f"Showing {len(filtered_df):,} of {len(df):,} comments")
    
    # Key Metrics Dashboard
    st.markdown("## 📊 Key Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_comments = len(filtered_df)
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E31837, #ff4757); color: white; padding: 1.5rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{total_comments:,}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Total Comments</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_quality = filtered_df['quality_score'].mean()
        quality_color = "#28a745" if avg_quality > 3.5 else "#ffc107" if avg_quality > 2.5 else "#dc3545"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {quality_color}, {quality_color}dd); color: white; padding: 1.5rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{avg_quality:.2f}</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Avg Quality</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        spam_rate = (filtered_df['is_spam'] == True).mean() * 100
        spam_color = "#28a745" if spam_rate < 10 else "#ffc107" if spam_rate < 20 else "#dc3545"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {spam_color}, {spam_color}dd); color: white; padding: 1.5rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{spam_rate:.1f}%</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Spam Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        positive_rate = (filtered_df['vader_sentiment'] == 'positive').mean() * 100
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #17a2b8, #20c997); color: white; padding: 1.5rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{positive_rate:.1f}%</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Positive Sentiment</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        genuine_rate = (filtered_df['relevance'] == 'genuine').mean() * 100
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #6f42c1, #e83e8c); color: white; padding: 1.5rem; border-radius: 16px; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold;">{genuine_rate:.1f}%</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">Genuine Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabbed visualization sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Engagement Analysis", 
        "😊 Sentiment Insights", 
        "⭐ Quality Metrics", 
        "🏷️ Beauty Categories",
        "🎥 Video Performance"
    ])
    
    with tab1:
        st.markdown("### 🎯 Comprehensive Engagement Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Enhanced engagement distribution
            engagement_counts = filtered_df['engagement_type'].value_counts()
            
            # Create a more detailed pie chart
            fig_engagement_pie = px.pie(
                values=engagement_counts.values,
                names=engagement_counts.index,
                title="Engagement Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_engagement_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
            fig_engagement_pie.update_layout(
                font=dict(size=12),
                showlegend=True,
                legend=dict(orientation="v", yanchor="middle", y=0.5)
            )
            st.plotly_chart(fig_engagement_pie, use_container_width=True)
        
        with col2:
            # Engagement vs Quality heatmap
            engagement_quality = filtered_df.groupby(['engagement_type', pd.cut(filtered_df['quality_score'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])]).size().reset_index(name='count')
            
            fig_heatmap = px.density_heatmap(
                engagement_quality,
                x='quality_score',
                y='engagement_type',
                z='count',
                title="Engagement Type vs Quality Score Heatmap",
                color_continuous_scale='Viridis'
            )
            fig_heatmap.update_layout(
                xaxis_title="Quality Score Range",
                yaxis_title="Engagement Type"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Detailed engagement metrics table
        st.markdown("#### 📋 Detailed Engagement Metrics")
        
        engagement_stats = filtered_df.groupby('engagement_type').agg({
            'quality_score': ['mean', 'std', 'count'],
            'vader_score': 'mean',
            'is_spam': lambda x: (x == True).mean() * 100
        }).round(3)
        
        engagement_stats.columns = ['Avg Quality', 'Quality Std', 'Count', 'Avg Sentiment Score', 'Spam Rate %']
        engagement_stats = engagement_stats.sort_values('Avg Quality', ascending=False)
        
        # Style the dataframe
        styled_engagement = engagement_stats.style.background_gradient(
            subset=['Avg Quality'], cmap='RdYlGn'
        ).background_gradient(
            subset=['Spam Rate %'], cmap='RdYlGn_r'
        ).format({
            'Avg Quality': '{:.2f}',
            'Quality Std': '{:.2f}',
            'Avg Sentiment Score': '{:.3f}',
            'Spam Rate %': '{:.1f}%'
        })
        
        st.dataframe(styled_engagement, use_container_width=True)
    
    with tab2:
        st.markdown("### 😊 Advanced Sentiment Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution with enhanced styling
            sentiment_counts = filtered_df['vader_sentiment'].value_counts()
            
            colors = {'positive': '#28a745', 'neutral': '#ffc107', 'negative': '#dc3545'}
            fig_sentiment = px.bar(
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                title="Sentiment Distribution",
                labels={'x': 'Sentiment', 'y': 'Number of Comments'},
                color=sentiment_counts.index,
                color_discrete_map=colors
            )
            fig_sentiment.update_layout(showlegend=False)
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Sentiment score distribution
            fig_sentiment_dist = px.histogram(
                filtered_df,
                x='vader_score',
                color='vader_sentiment',
                title="Sentiment Score Distribution",
                nbins=30,
                color_discrete_map=colors
            )
            fig_sentiment_dist.update_layout(
                xaxis_title="VADER Sentiment Score",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_sentiment_dist, use_container_width=True)
        
        # Sentiment vs Engagement cross-analysis
        st.markdown("#### 🔄 Sentiment vs Engagement Cross-Analysis")
        
        sentiment_engagement = pd.crosstab(
            filtered_df['vader_sentiment'], 
            filtered_df['engagement_type'], 
            normalize='columns'
        ) * 100
        
        fig_cross = px.imshow(
            sentiment_engagement.values,
            x=sentiment_engagement.columns,
            y=sentiment_engagement.index,
            color_continuous_scale='RdYlBu',
            title="Sentiment Distribution by Engagement Type (%)",
            text_auto='.1f'
        )
        fig_cross.update_layout(
            xaxis_title="Engagement Type",
            yaxis_title="Sentiment"
        )
        st.plotly_chart(fig_cross, use_container_width=True)
        
        # Sentiment insights
        st.markdown("#### 💡 Sentiment Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            most_positive_engagement = filtered_df[filtered_df['vader_sentiment'] == 'positive']['engagement_type'].mode()
            if len(most_positive_engagement) > 0:
                st.success(f"**Most Positive Engagement:** {most_positive_engagement.iloc[0]}")
        
        with col2:
            avg_positive_quality = filtered_df[filtered_df['vader_sentiment'] == 'positive']['quality_score'].mean()
            st.info(f"**Avg Quality (Positive):** {avg_positive_quality:.2f}")
        
        with col3:
            negative_rate = (filtered_df['vader_sentiment'] == 'negative').mean() * 100
            st.warning(f"**Negative Rate:** {negative_rate:.1f}%")
    
    with tab3:
        st.markdown("### ⭐ Comment Quality Analysis")
        
        # Quality Overview Section
        st.markdown("#### 🎯 Quality Overview")
        
        # Calculate quality metrics
        avg_quality = filtered_df['quality_score'].mean()
        quality_std = filtered_df['quality_score'].std()
        
        # Quality ranges with better names and icons
        quality_ranges = {
            '🌟 Excellent': {
                'range': (4.0, 5.0),
                'color': '#28a745',
                'description': 'High-value, engaging comments'
            },
            '👍 Good': {
                'range': (3.0, 4.0),
                'color': '#20c997',
                'description': 'Positive, meaningful interactions'
            },
            '😐 Average': {
                'range': (2.0, 3.0),
                'color': '#ffc107',
                'description': 'Basic engagement, room for improvement'
            },
            '👎 Below Average': {
                'range': (1.0, 2.0),
                'color': '#fd7e14',
                'description': 'Low-quality or minimal engagement'
            },
            '🚫 Poor': {
                'range': (0.0, 1.0),
                'color': '#dc3545',
                'description': 'Spam, irrelevant, or harmful content'
            }
        }
        
        # Calculate counts for each range
        for category, info in quality_ranges.items():
            min_val, max_val = info['range']
            if category == '🌟 Excellent':
                count = ((filtered_df['quality_score'] >= min_val) & (filtered_df['quality_score'] <= max_val)).sum()
            else:
                count = ((filtered_df['quality_score'] >= min_val) & (filtered_df['quality_score'] < max_val)).sum()
            info['count'] = count
            info['percentage'] = (count / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
        
        # Create a more readable donut chart
        categories = list(quality_ranges.keys())
        values = [quality_ranges[cat]['count'] for cat in categories]
        colors_list = [quality_ranges[cat]['color'] for cat in categories]
        
        fig_quality_donut = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=0.4,
            marker_colors=colors_list,
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='<b>%{label}</b><br>' +
                         'Count: %{value}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig_quality_donut.update_layout(
            title={
                'text': "Comment Quality Distribution",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18}
            },
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.01
            ),
            height=400,
            margin=dict(t=50, b=50, l=50, r=150)
        )
        
        # Add center text showing average quality
        fig_quality_donut.add_annotation(
            text=f"Avg Quality<br><b>{avg_quality:.1f}/5</b>",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )
        
        st.plotly_chart(fig_quality_donut, use_container_width=True)
        
        # Quality Breakdown Cards
        st.markdown("#### 📊 Quality Breakdown")
        
        # Create responsive columns based on screen size
        cols = st.columns(len(quality_ranges))
        
        for i, (category, info) in enumerate(quality_ranges.items()):
            with cols[i]:
                # Create gradient effect
                gradient_color = info['color']
                
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, {gradient_color}, {gradient_color}dd);
                    color: white;
                    padding: 1.5rem;
                    border-radius: 16px;
                    text-align: center;
                    margin-bottom: 1rem;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                ">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{category.split()[0]}</div>
                    <div style="font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;">{info['count']:,}</div>
                    <div style="font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem;">{info['percentage']:.1f}%</div>
                    <div style="font-size: 0.85rem; opacity: 0.9; line-height: 1.3;">{info['description']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Quality Insights Section
        st.markdown("#### 💡 Quality Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quality gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = avg_quality,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Quality Score"},
                delta = {'reference': 3.0, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
                gauge = {
                    'axis': {'range': [None, 5]},
                    'bar': {'color': "#E31837"},
                    'steps': [
                        {'range': [0, 2], 'color': "#ffcccc"},
                        {'range': [2, 3], 'color': "#ffffcc"},
                        {'range': [3, 4], 'color': "#ccffcc"},
                        {'range': [4, 5], 'color': "#ccffff"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 4.0
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            # Quality by engagement type - simplified bar chart
            engagement_quality = filtered_df.groupby('engagement_type')['quality_score'].mean().sort_values(ascending=True)
            
            fig_engagement_quality = px.bar(
                x=engagement_quality.values,
                y=engagement_quality.index,
                orientation='h',
                title="Average Quality by Engagement Type",
                color=engagement_quality.values,
                color_continuous_scale='RdYlGn',
                text=engagement_quality.values.round(2)
            )
            
            fig_engagement_quality.update_traces(textposition='outside')
            fig_engagement_quality.update_layout(
                xaxis_title="Average Quality Score",
                yaxis_title="Engagement Type",
                showlegend=False,
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig_engagement_quality, use_container_width=True)
        
        # Quality Recommendations
        st.markdown("#### 🎯 Quality Improvement Recommendations")
        
        # Generate recommendations based on data
        recommendations = []
        
        excellent_rate = quality_ranges['🌟 Excellent']['percentage']
        poor_rate = quality_ranges['🚫 Poor']['percentage']
        
        if excellent_rate > 40:
            recommendations.append({
                'icon': '🌟',
                'title': 'Excellent Performance',
                'message': f'{excellent_rate:.1f}% of comments are excellent quality. Keep up the great work!',
                'type': 'success'
            })
        elif excellent_rate < 20:
            recommendations.append({
                'icon': '📈',
                'title': 'Boost High-Quality Engagement',
                'message': f'Only {excellent_rate:.1f}% excellent comments. Try more engaging call-to-actions.',
                'type': 'warning'
            })
        
        if poor_rate > 20:
            recommendations.append({
                'icon': '🛡️',
                'title': 'Improve Content Moderation',
                'message': f'{poor_rate:.1f}% poor quality comments detected. Consider stricter moderation.',
                'type': 'error'
            })
        elif poor_rate < 10:
            recommendations.append({
                'icon': '✅',
                'title': 'Great Community Health',
                'message': f'Low poor-quality rate ({poor_rate:.1f}%). Your community is well-managed.',
                'type': 'success'
            })
        
        if avg_quality > 3.5:
            recommendations.append({
                'icon': '🎯',
                'title': 'Maintain Quality Standards',
                'message': f'High average quality ({avg_quality:.1f}/5). Focus on consistency.',
                'type': 'info'
            })
        elif avg_quality < 2.5:
            recommendations.append({
                'icon': '🔧',
                'title': 'Quality Enhancement Needed',
                'message': f'Average quality is {avg_quality:.1f}/5. Consider content strategy improvements.',
                'type': 'warning'
            })
        
        # Display recommendations
        for rec in recommendations:
            if rec['type'] == 'success':
                st.success(f"{rec['icon']} **{rec['title']}**: {rec['message']}")
            elif rec['type'] == 'warning':
                st.warning(f"{rec['icon']} **{rec['title']}**: {rec['message']}")
            elif rec['type'] == 'error':
                st.error(f"{rec['icon']} **{rec['title']}**: {rec['message']}")
            else:
                st.info(f"{rec['icon']} **{rec['title']}**: {rec['message']}")
        
        # Quality Statistics Table
        st.markdown("#### 📋 Quality Statistics Summary")
        
        quality_stats = pd.DataFrame({
            'Metric': ['Average Quality', 'Standard Deviation', 'Median Quality', 'Highest Quality', 'Lowest Quality'],
            'Value': [
                f"{avg_quality:.2f}/5",
                f"{quality_std:.2f}",
                f"{filtered_df['quality_score'].median():.2f}/5",
                f"{filtered_df['quality_score'].max():.2f}/5",
                f"{filtered_df['quality_score'].min():.2f}/5"
            ],
            'Interpretation': [
                'Overall comment quality level',
                'Quality consistency (lower = more consistent)',
                'Middle point of quality distribution',
                'Best comment quality achieved',
                'Lowest quality comment found'
            ]
        })
        
        st.dataframe(quality_stats, use_container_width=True, hide_index=True)
    
    with tab4:
        st.markdown("### 🏷️ Beauty Category Analysis")
        
        if 'beauty_category' in filtered_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Category distribution pie chart
                category_counts = filtered_df['beauty_category'].value_counts()
                
                # Define colors for each category
                category_colors = {
                    'makeup': '#E31837',
                    'skincare': '#28a745', 
                    'fragrance': '#6f42c1',
                    'haircare': '#fd7e14',
                    'nails': '#e83e8c',
                    'tools_accessories': '#20c997',
                    'general': '#6c757d'
                }
                
                colors = [category_colors.get(cat, '#6c757d') for cat in category_counts.index]
                
                fig_category_pie = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Beauty Category Distribution",
                    color_discrete_sequence=colors
                )
                fig_category_pie.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )
                st.plotly_chart(fig_category_pie, use_container_width=True)
            
            with col2:
                # Category vs Quality heatmap
                if len(category_counts) > 1:
                    category_quality = filtered_df.groupby(['beauty_category', pd.cut(filtered_df['quality_score'], bins=5, labels=['Very Low', 'Low', 'Medium', 'High', 'Very High'])]).size().reset_index(name='count')
                    
                    fig_cat_heatmap = px.density_heatmap(
                        category_quality,
                        x='quality_score',
                        y='beauty_category',
                        z='count',
                        title="Category vs Quality Score Heatmap",
                        color_continuous_scale='Viridis'
                    )
                    fig_cat_heatmap.update_layout(
                        xaxis_title="Quality Score Range",
                        yaxis_title="Beauty Category"
                    )
                    st.plotly_chart(fig_cat_heatmap, use_container_width=True)
            
            # Category performance metrics
            st.markdown("#### 📊 Category Performance Metrics")
            
            category_stats = filtered_df.groupby('beauty_category').agg({
                'quality_score': ['mean', 'std', 'count'],
                'vader_score': 'mean',
                'is_spam': lambda x: (x == True).mean() * 100,
                'category_confidence': 'mean' if 'category_confidence' in filtered_df.columns else lambda x: 0
            }).round(3)
            
            if 'category_confidence' in filtered_df.columns:
                category_stats.columns = ['Avg Quality', 'Quality Std', 'Count', 'Avg Sentiment', 'Spam Rate %', 'Avg Confidence']
            else:
                category_stats.columns = ['Avg Quality', 'Quality Std', 'Count', 'Avg Sentiment', 'Spam Rate %']
            
            category_stats = category_stats.sort_values('Avg Quality', ascending=False)
            
            # Style the dataframe
            styled_categories = category_stats.style.background_gradient(
                subset=['Avg Quality'], cmap='RdYlGn'
            ).background_gradient(
                subset=['Spam Rate %'], cmap='RdYlGn_r'
            )
            
            if 'Avg Confidence' in category_stats.columns:
                styled_categories = styled_categories.background_gradient(
                    subset=['Avg Confidence'], cmap='Blues'
                )
            
            st.dataframe(styled_categories, use_container_width=True)
            
            # Category insights
            st.markdown("#### 💡 Category Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                top_category = category_counts.index[0]
                top_percentage = (category_counts.iloc[0] / len(filtered_df)) * 100
                st.success(f"**Most Discussed:** {top_category.title()} ({top_percentage:.1f}%)")
            
            with col2:
                if len(category_stats) > 0:
                    highest_quality_cat = category_stats.index[0]
                    highest_quality_score = category_stats.iloc[0]['Avg Quality']
                    st.info(f"**Highest Quality:** {highest_quality_cat.title()} ({highest_quality_score:.2f})")
            
            with col3:
                if 'category_confidence' in filtered_df.columns:
                    avg_confidence = filtered_df['category_confidence'].mean()
                    st.warning(f"**Avg Confidence:** {avg_confidence:.2f}")
            
            # Detailed category breakdown
            st.markdown("#### 🔍 Detailed Category Breakdown")
            
            for category in category_counts.index[:5]:  # Top 5 categories
                category_data = filtered_df[filtered_df['beauty_category'] == category]
                
                with st.expander(f"📋 {category.title()} Analysis ({len(category_data)} comments)"):
                    
                    # Category-specific metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        avg_qual = category_data['quality_score'].mean()
                        st.metric("Avg Quality", f"{avg_qual:.2f}")
                    
                    with col2:
                        pos_sent = (category_data['vader_sentiment'] == 'positive').mean() * 100
                        st.metric("Positive %", f"{pos_sent:.1f}%")
                    
                    with col3:
                        spam_rate = (category_data['is_spam'] == True).mean() * 100
                        st.metric("Spam Rate", f"{spam_rate:.1f}%")
                    
                    with col4:
                        if 'category_confidence' in category_data.columns:
                            conf = category_data['category_confidence'].mean()
                            st.metric("Confidence", f"{conf:.2f}")
                    
                    # Top engagement types for this category
                    top_engagements = category_data['engagement_type'].value_counts().head(3)
                    st.write("**Top Engagement Types:**")
                    for eng_type, count in top_engagements.items():
                        percentage = (count / len(category_data)) * 100
                        st.write(f"• {eng_type}: {count} ({percentage:.1f}%)")
                    
                    # Sample comments for this category
                    if len(category_data) > 0:
                        st.write("**Sample Comments:**")
                        sample_comments = category_data.nlargest(3, 'quality_score')['textOriginal_cleaned'].tolist()
                        for i, comment in enumerate(sample_comments, 1):
                            if len(comment) > 100:
                                comment = comment[:100] + "..."
                            st.write(f"{i}. {comment}")
        
        else:
            st.info("Beauty category analysis not available. The enhanced analyzer will automatically categorize comments in future analyses.")
            
            # Show instructions for enabling categories
            st.markdown("""
            #### 🔧 How to Enable Beauty Categories
            
            Beauty category analysis is automatically included when you:
            1. **Re-analyze your data** with the enhanced analyzer
            2. **Upload new data** - categories will be detected automatically
            
            **Categories detected:**
            - 🎨 **Makeup**: Foundation, eyeshadow, lipstick, etc.
            - 🧴 **Skincare**: Serums, moisturizers, cleansers, etc.  
            - 🌸 **Fragrance**: Perfumes, scents, fragrance reviews
            - 💇 **Haircare**: Shampoo, styling, hair treatments
            - 💅 **Nails**: Nail polish, nail art, manicures
            - 🛠️ **Tools & Accessories**: Brushes, mirrors, applicators
            - 📝 **General**: Non-specific beauty discussions
            """)
    
    with tab5:
        st.markdown("### 🎥 Video Performance")
        
        if 'title' in filtered_df.columns:
            # Simple video analysis
            video_stats = filtered_df.groupby('title').agg({
                'quality_score': 'mean',
                'textOriginal_cleaned': 'count',
                'vader_sentiment': lambda x: (x == 'positive').mean() * 100,
                'is_spam': lambda x: (x == True).mean() * 100
            }).round(2)
            
            video_stats.columns = ['Quality Score', 'Comments', 'Positive %', 'Spam %']
            video_stats = video_stats.reset_index()
            
            # Overview metrics
            st.markdown("#### 📊 Quick Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_videos = len(video_stats)
                st.metric("Total Videos", f"{total_videos}")
            
            with col2:
                avg_quality = video_stats['Quality Score'].mean()
                st.metric("Average Quality", f"{avg_quality:.1f}/5")
            
            with col3:
                avg_comments = video_stats['Comments'].mean()
                st.metric("Average Comments", f"{avg_comments:.0f}")
            
            # Top performing videos
            st.markdown("#### 🏆 Top Performing Videos")
            
            # Sort by quality score
            top_videos = video_stats.nlargest(5, 'Quality Score')
            
            # Simple bar chart
            fig_top = px.bar(
                top_videos,
                x='Quality Score',
                y='title',
                orientation='h',
                title="Top 5 Videos by Quality Score",
                color='Quality Score',
                color_continuous_scale='RdYlGn',
                text='Quality Score'
            )
            
            fig_top.update_traces(textposition='outside')
            fig_top.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig_top, use_container_width=True)
            
            # Simple performance table
            st.markdown("#### 📋 Video Performance Summary")
            
            # Add performance indicators
            def get_performance_indicator(quality, spam_rate):
                if quality >= 4.0 and spam_rate < 10:
                    return "🌟 Excellent"
                elif quality >= 3.0 and spam_rate < 20:
                    return "👍 Good"
                elif quality >= 2.0:
                    return "😐 Average"
                else:
                    return "👎 Needs Work"
            
            video_stats['Performance'] = video_stats.apply(
                lambda row: get_performance_indicator(row['Quality Score'], row['Spam %']), 
                axis=1
            )
            
            # Display simplified table
            display_df = video_stats[['title', 'Quality Score', 'Comments', 'Positive %', 'Performance']].copy()
            display_df.columns = ['Video Title', 'Quality', 'Comments', 'Positive %', 'Status']
            
            # Truncate long titles
            display_df['Video Title'] = display_df['Video Title'].apply(
                lambda x: x[:50] + "..." if len(x) > 50 else x
            )
            
            st.dataframe(
                display_df.sort_values('Quality', ascending=False),
                use_container_width=True,
                hide_index=True
            )
            
            # Simple insights
            st.markdown("#### 💡 Key Insights")
            
            excellent_count = (video_stats['Performance'] == '🌟 Excellent').sum()
            needs_work_count = (video_stats['Performance'] == '👎 Needs Work').sum()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if excellent_count > 0:
                    st.success(f"🌟 {excellent_count} videos performing excellently!")
                else:
                    st.info("💡 Focus on improving video quality scores")
            
            with col2:
                if needs_work_count > 0:
                    st.warning(f"⚠️ {needs_work_count} videos need attention")
                else:
                    st.success("✅ All videos performing well!")
            
            # Best and worst performers
            if len(video_stats) > 1:
                best_video = video_stats.loc[video_stats['Quality Score'].idxmax()]
                worst_video = video_stats.loc[video_stats['Quality Score'].idxmin()]
                
                st.markdown("#### 🎯 Performance Highlights")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **🏆 Best Performer:**
                    - **Video:** {best_video['title'][:40]}...
                    - **Quality:** {best_video['Quality Score']:.1f}/5
                    - **Comments:** {best_video['Comments']:,}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **📈 Improvement Opportunity:**
                    - **Video:** {worst_video['title'][:40]}...
                    - **Quality:** {worst_video['Quality Score']:.1f}/5
                    - **Comments:** {worst_video['Comments']:,}
                    """)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 20px; margin: 2rem 0;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📹</div>
                <h3 style="color: #6c757d; margin-bottom: 1rem;">Video Analysis Not Available</h3>
                <p style="color: #6c757d;">Video title information is required for video performance analysis. Please ensure your dataset includes video metadata.</p>
            </div>
            """, unsafe_allow_html=True)




def ai_assistant_page():
    """Simple AI Assistant page for asking questions about your data"""
    
    # Enhanced Header
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa, #ffffff); border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🤖</div>
        <h1 style="margin: 0; color: #E31837; font-size: 2.5rem;">AI Assistant</h1>
        <p style="margin: 1rem 0 0 0; color: #6c757d; font-size: 1.2rem;">Ask questions about your comment analysis data</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    ai_assistant = AIAssistant(df)
    
    # AI Status
    st.markdown("### 🔧 AI Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        api_key = st.secrets["api_keys"]["api_key"]
        st.metric("API Key", "✅ Configured" if api_key else "❌ Missing")
    
    with col2:
        st.metric("AI Status", "✅ Ready" if ai_assistant.is_gemini_enabled else "⚠️ Basic Mode")
    
    with col3:
        model_name = "Gemini AI" if ai_assistant.is_gemini_enabled else "Rule-based"
        st.metric("AI Model", model_name)
    
    if not api_key:
        st.info("💡 **Tip:** Add your Gemini API key to `.env` file for enhanced AI responses: `GEMINI_API_KEY=your_key_here`")
    
    # Quick Data Overview
    st.markdown("### 📊 Your Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_comments = len(df)
    spam_rate = (df.get('is_spam', pd.Series()) == True).mean() * 100
    avg_quality = df.get('quality_score', pd.Series()).mean()
    positive_rate = (df.get('vader_sentiment', pd.Series()) == 'positive').mean() * 100
    
    with col1:
        st.metric("Total Comments", f"{total_comments:,}")
    with col2:
        st.metric("Spam Rate", f"{spam_rate:.1f}%")
    with col3:
        st.metric("Quality Score", f"{avg_quality:.1f}/5")
    with col4:
        st.metric("Positive Sentiment", f"{positive_rate:.1f}%")
    
    # Chat Interface
    st.markdown("### 💬 Ask Your AI Assistant")
    
    # Initialize chat history
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []
    
    # Display chat history
    if st.session_state.ai_chat_history:
        st.markdown("#### 📝 Conversation History")
        
        for i, (question, answer) in enumerate(st.session_state.ai_chat_history):
            # User message
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 1rem; border-radius: 15px 15px 5px 15px; margin: 10px 0; margin-left: 50px; border-left: 4px solid #6c757d;">
                <strong>🙋 You:</strong> {question}
            </div>
            """, unsafe_allow_html=True)
            
            # AI response
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #E31837, #ff4757); color: white; padding: 1rem; border-radius: 15px 15px 15px 5px; margin: 10px 0; margin-right: 50px;">
                <strong>🤖 AI:</strong> {answer}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #E31837, #ff4757); color: white; padding: 2rem; border-radius: 20px; margin: 2rem 0; text-align: center; box-shadow: 0 8px 30px rgba(227, 24, 55, 0.3);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="margin: 0 0 1rem 0;">Welcome! I'm your AI Assistant</h3>
            <p style="margin: 0; opacity: 0.9; font-size: 1.1rem;">I can analyze your comment data and answer questions about spam rates, sentiment, engagement patterns, and provide recommendations. What would you like to know?</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Action Buttons
    st.markdown("#### ⚡ Quick Questions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Data Summary", use_container_width=True):
            question = "Give me a summary of my comment data"
            with st.spinner("🤖 Analyzing..."):
                answer = ai_assistant.answer_question(question)
                st.session_state.ai_chat_history.append((question, answer))
                st.rerun()
    
    with col2:
        if st.button("🛡️ Spam Analysis", use_container_width=True):
            question = "What's my spam rate and how can I improve it?"
            with st.spinner("🤖 Analyzing..."):
                answer = ai_assistant.answer_question(question)
                st.session_state.ai_chat_history.append((question, answer))
                st.rerun()
    
    with col3:
        if st.button("😊 Sentiment Check", use_container_width=True):
            question = "How is my audience sentiment?"
            with st.spinner("🤖 Analyzing..."):
                answer = ai_assistant.answer_question(question)
                st.session_state.ai_chat_history.append((question, answer))
                st.rerun()
    
    with col4:
        if st.button("💡 Get Recommendations", use_container_width=True):
            question = "What are your top recommendations for improving my content?"
            with st.spinner("🤖 Analyzing..."):
                answer = ai_assistant.answer_question(question)
                st.session_state.ai_chat_history.append((question, answer))
                st.rerun()
    
    # Custom Question Input
    st.markdown("#### 💭 Ask Your Own Question")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_question = st.text_input(
            "Type your question:",
            placeholder="e.g., What trends do you see in my comments? How can I reduce spam?",
            key="custom_ai_question"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button("🚀 Ask AI", type="primary", use_container_width=True)
    
    # Response mode selection
    response_mode = st.radio(
        "Response Style:",
        ["🚀 Quick & Concise", "📝 Detailed Analysis"],
        horizontal=True,
        help="Choose between short answers or detailed explanations"
    )
    
    # Process custom question
    if ask_button and user_question:
        with st.spinner("🤖 AI is thinking..."):
            try:
                if response_mode == "🚀 Quick & Concise":
                    answer = ai_assistant.get_short_answer(user_question)
                else:
                    answer = ai_assistant.answer_question(user_question)
                
                st.session_state.ai_chat_history.append((user_question, answer))
                st.rerun()
            except Exception as e:
                st.error(f"AI Assistant error: {e}")
    
    # Suggested Questions
    with st.expander("💡 Need inspiration? Try these questions:", expanded=False):
        suggested_questions = [
            "What's my overall comment quality?",
            "Which engagement type is most common?",
            "How can I improve my content strategy?",
            "What are the main topics in my comments?",
            "Are there any concerning patterns in my data?",
            "What's working well in my content?",
            "How does my performance compare to benchmarks?",
            "What should I focus on next?"
        ]
        
        cols = st.columns(2)
        for i, question in enumerate(suggested_questions):
            col = cols[i % 2]
            if col.button(f"💭 {question}", key=f"suggested_q_{i}", use_container_width=True):
                with st.spinner("🤖 AI is thinking..."):
                    try:
                        if response_mode == "🚀 Quick & Concise":
                            answer = ai_assistant.get_short_answer(question)
                        else:
                            answer = ai_assistant.answer_question(question)
                        
                        st.session_state.ai_chat_history.append((question, answer))
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI Assistant error: {e}")
    
    # Chat Management
    if st.session_state.ai_chat_history:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.ai_chat_history = []
                st.success("Chat history cleared!")
                st.rerun()
        
        with col2:
            # Export chat
            chat_export = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in st.session_state.ai_chat_history])
            st.download_button(
                "📋 Export Chat History",
                chat_export,
                file_name=f"ai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

def export_page():
    st.header("📋 Data Export")
    
    if not st.session_state.analysis_complete:
        st.warning("⚠️ Please upload and analyze data first!")
        return
    
    df = st.session_state.analysis_results
    
    st.subheader("💾 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV Export
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📄 Download Full Results (CSV)",
            data=csv_data,
            file_name=f"loreal_comment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # Summary Report
        try:
            dashboard = CommentDashboard(df)
            insights = dashboard.generate_insights()
            
            # Generate summary report
            total_comments = len(df)
            spam_rate = (df['is_spam'] == True).mean() * 100
            avg_quality = df['quality_score'].mean()
            
            sentiment_dist = df['vader_sentiment'].value_counts(normalize=True) * 100
            relevance_dist = df['relevance'].value_counts(normalize=True) * 100
            
            report = f"""L'ORÉAL YOUTUBE COMMENT ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===============================================

OVERVIEW
--------
Total Comments: {total_comments:,}
Average Quality Score: {avg_quality:.2f}/5
Spam Rate: {spam_rate:.1f}%

RELEVANCE BREAKDOWN
------------------
"""
            
            for category, percentage in relevance_dist.items():
                report += f"{category.title()}: {percentage:.1f}%\n"
            
            report += "\nSENTIMENT ANALYSIS\n-----------------\n"
            
            for sentiment, percentage in sentiment_dist.items():
                report += f"{sentiment.title()}: {percentage:.1f}%\n"
            
            report += "\nKEY INSIGHTS\n-----------\n"
            
            for insight in insights:
                report += f"• {insight}\n"
            
            st.download_button(
                label="📊 Download Summary Report (TXT)",
                data=report,
                file_name=f"loreal_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Error generating report: {e}")
    
    # Data preview
    st.subheader("👀 Data Preview")
    
    # Show column selection
    all_columns = df.columns.tolist()
    selected_columns = st.multiselect(
        "Select columns to preview:",
        all_columns,
        default=['textOriginal_cleaned', 'relevance', 'vader_sentiment', 'engagement_type', 'quality_score'][:5]
    )
    
    if selected_columns:
        st.dataframe(df[selected_columns].head(20), use_container_width=True)
    
    # Statistics
    st.subheader("📈 Quick Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Relevance Distribution**")
        st.write(df['relevance'].value_counts())
    
    with col2:
        st.write("**Sentiment Distribution**")
        st.write(df['vader_sentiment'].value_counts())
    
    with col3:
        st.write("**Engagement Types**")
        st.write(df['engagement_type'].value_counts().head())

if __name__ == "__main__":
    main()