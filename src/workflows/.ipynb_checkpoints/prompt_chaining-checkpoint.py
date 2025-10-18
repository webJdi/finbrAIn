# src/workflows/prompt_chaining.py
from typing import Dict, List
import json

class PromptChainingWorkflow:
    """Implement Prompt Chaining: Ingest News → Preprocess → Classify → Extract → Summarize"""
    
    def __init__(self, model):
        self.model = model
    
    def ingest_news(self, symbol: str) -> List[Dict]:
        """Ingest news for a given symbol"""
        # Placeholder - integrate with actual news API
        return [
            {'title': f'{symbol} reports strong earnings', 'content': '...', 'source': 'Reuters'},
            {'title': f'Market analysis for {symbol}', 'content': '...', 'source': 'Bloomberg'}
        ]
    
    def preprocess_news(self, news_items: List[Dict]) -> List[Dict]:
        """Preprocess news content"""
        processed = []
        for item in news_items:
            processed.append({
                'title': item['title'].strip(),
                'content': item['content'][:500] + '...' if len(item['content']) > 500 else item['content'],
                'source': item['source'],
                'length': len(item['content'])
            })
        return processed
    
    def classify_sentiment(self, news_items: List[Dict]) -> List[Dict]:
        """Classify news sentiment"""
        classified = []
        for item in news_items:
            # Simple rule-based classification (enhance with LLM)
            title_lower = item['title'].lower()
            if any(word in title_lower for word in ['strong', 'beat', 'growth', 'profit']):
                sentiment = 'positive'
            elif any(word in title_lower for word in ['weak', 'miss', 'loss', 'decline']):
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
                
            classified.append({**item, 'sentiment': sentiment})
        return classified
    
    def extract_key_points(self, classified_news: List[Dict]) -> Dict:
        """Extract key points from classified news"""
        positive_news = [item for item in classified_news if item['sentiment'] == 'positive']
        negative_news = [item for item in classified_news if item['sentiment'] == 'negative']
        
        return {
            'total_news': len(classified_news),
            'positive_count': len(positive_news),
            'negative_count': len(negative_news),
            'key_positive_points': [item['title'] for item in positive_news[:3]],
            'key_negative_points': [item['title'] for item in negative_news[:3]]
        }
    
    def summarize_analysis(self, extracted_points: Dict) -> str:
        """Generate summary analysis"""
        return f"""
        News Analysis Summary:
        - Total articles analyzed: {extracted_points['total_news']}
        - Positive sentiment: {extracted_points['positive_count']} articles
        - Negative sentiment: {extracted_points['negative_count']} articles
        
        Key Positive Developments:
        {chr(10).join(['• ' + point for point in extracted_points['key_positive_points']])}
        
        Key Concerns:
        {chr(10).join(['• ' + point for point in extracted_points['key_negative_points']])}
        """
    
    def execute_chain(self, symbol: str) -> Dict:
        """Execute the complete prompt chaining workflow"""
        news = self.ingest_news(symbol)
        processed = self.preprocess_news(news)
        classified = self.classify_sentiment(processed)
        extracted = self.extract_key_points(classified)
        summary = self.summarize_analysis(extracted)
        
        return {
            'workflow': 'prompt_chaining',
            'symbol': symbol,
            'stages': {
                'ingested_news': len(news),
                'processed_items': len(processed),
                'classified_items': len(classified)
            },
            'summary': summary,
            'detailed_analysis': extracted
        }