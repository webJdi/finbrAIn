# src/tools/data_fetchers.py
import yfinance as yf
import pandas as pd
import requests
from typing import Dict, List, Optional
import json

class FinancialDataFetcher:
    """Tool for fetching financial data from various sources"""
    
    @staticmethod
    def get_stock_data(symbol: str, period: str = "1y") -> Dict:
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period=period)
            
            return {
                'symbol': symbol,
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'company_name': info.get('longName'),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'price_history': hist.to_dict('records') if not hist.empty else [],
                'financials': {
                    'revenue': info.get('totalRevenue'),
                    'profit_margin': info.get('profitMargins'),
                    'debt_to_equity': info.get('debtToEquity')
                }
            }
        except Exception as e:
            return {'error': f"Failed to fetch data for {symbol}: {str(e)}"}
    
    @staticmethod
    def get_news_sentiment(symbol: str, api_key: Optional[str] = None) -> List[Dict]:
        """Fetch news sentiment for a stock (placeholder implementation)"""
        # In practice, you'd integrate with NewsAPI or similar
        return [
            {
                'title': f'Latest developments for {symbol}',
                'sentiment': 'neutral',
                'confidence': 0.7
            }
        ]