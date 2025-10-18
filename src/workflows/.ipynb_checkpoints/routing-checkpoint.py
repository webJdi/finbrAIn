# src/workflows/routing.py
from typing import Dict, Any
import json

class RoutingWorkflow:
    """Implement Routing: Direct content to the right specialist analyzer"""
    
    def __init__(self, model):
        self.model = model
        self.analyzers = {
            'earnings': EarningsAnalyzer(),
            'news': NewsAnalyzer(), 
            'market': MarketAnalyzer()
        }
    
    def route_content(self, content: str, content_type: str) -> Dict:
        """Route content to appropriate analyzer"""
        if 'earnings' in content_type.lower() or 'financial' in content_type.lower():
            analyzer = self.analyzers['earnings']
        elif 'news' in content_type.lower() or 'article' in content_type.lower():
            analyzer = self.analyzers['news']
        else:
            analyzer = self.analyzers['market']
        
        return analyzer.analyze(content)
    
    def auto_route(self, content: str) -> Dict:
        """Automatically detect content type and route"""
        # Simple content type detection
        content_lower = content.lower()
        
        if any(term in content_lower for term in ['earnings', 'revenue', 'profit', 'eps']):
            content_type = 'earnings'
        elif any(term in content_lower for term in ['news', 'report', 'article', 'update']):
            content_type = 'news'
        else:
            content_type = 'market'
        
        return self.route_content(content, content_type)

class EarningsAnalyzer:
    def analyze(self, content: str) -> Dict:
        return {
            'analyzer': 'earnings',
            'analysis': 'Earnings analysis performed',
            'metrics_extracted': ['revenue', 'eps', 'guidance'],
            'confidence': 0.9
        }

class NewsAnalyzer:
    def analyze(self, content: str) -> Dict:
        return {
            'analyzer': 'news', 
            'analysis': 'News sentiment analysis performed',
            'sentiment': 'neutral',
            'key_entities': ['company', 'executives', 'products']
        }

class MarketAnalyzer:
    def analyze(self, content: str) -> Dict:
        return {
            'analyzer': 'market',
            'analysis': 'Market trend analysis performed',
            'trend': 'stable',
            'factors': ['market conditions', 'sector performance']
        }