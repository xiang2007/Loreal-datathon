"""
L'Oréal YouTube Comment Analysis - Core Modules
"""

from .data_processing import DataProcessor
from .analysis import CommentAnalyzer
from .dashboard import CommentDashboard
from .ai_assistant import AIAssistant

__all__ = ['DataProcessor', 'CommentAnalyzer', 'CommentDashboard', 'AIAssistant']