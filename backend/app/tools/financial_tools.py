from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import yfinance as yf
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from functools import lru_cache
import asyncio
import aiohttp

class BaseTool(ABC):
    """Base class for all financial data tools"""
    
    @abstractmethod
    async def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:
        pass

class YahooFinanceTool(BaseTool):
    """Tool for fetching data from Yahoo Finance"""
    
    async def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """Fetch comprehensive financial data from Yahoo Finance"""
        try:
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch various data points
            info = ticker.info
            history = ticker.history(period="1y")
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            return {
                "symbol": symbol,
                "company_info": {
                    "name": info.get("longName", "N/A"),
                    "sector": info.get("sector", "N/A"),
                    "industry": info.get("industry", "N/A"),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "forward_pe": info.get("forwardPE", 0),
                    "peg_ratio": info.get("pegRatio", 0),
                    "price_to_book": info.get("priceToBook", 0),
                    "debt_to_equity": info.get("debtToEquity", 0),
                    "return_on_equity": info.get("returnOnEquity", 0),
                    "profit_margin": info.get("profitMargins", 0),
                    "revenue_growth": info.get("revenueGrowth", 0),
                },
                "price_data": {
                    "current_price": info.get("currentPrice", 0),
                    "previous_close": info.get("previousClose", 0),
                    "day_high": info.get("dayHigh", 0),
                    "day_low": info.get("dayLow", 0),
                    "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                    "52_week_low": info.get("fiftyTwoWeekLow", 0),
                    "volume": info.get("volume", 0),
                    "avg_volume": info.get("averageVolume", 0),
                },
                "historical_data": history.tail(30).to_dict('records') if not history.empty else [],
                "recommendation": info.get("recommendationKey", "N/A"),
                "target_price": info.get("targetMeanPrice", 0),
                "analyst_count": info.get("numberOfAnalystOpinions", 0),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class NewsAPITool(BaseTool):
    """Tool for fetching financial news"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWS_API_KEY")
        self.base_url = "https://newsapi.org/v2/everything"
    
    async def fetch_data(self, symbol: str, **kwargs) -> Dict[str, Any]:
        """Fetch news articles related to the stock symbol"""
        if not self.api_key:
            return {"error": "NEWS_API_KEY not configured", "articles": []}
        
        try:
            # Get company name for better search
            ticker = yf.Ticker(symbol)
            company_name = ticker.info.get("longName", symbol)
            
            # Prepare search query
            query = f'"{company_name}" OR "{symbol}" AND (stock OR shares OR financial OR earnings)'
            
            params = {
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 20,
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                "apiKey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
            
            if data.get("status") == "ok":
                articles = []
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "published_at": article.get("publishedAt"),
                        "source": article.get("source", {}).get("name"),
                    })
                
                return {
                    "symbol": symbol,
                    "company_name": company_name,
                    "articles": articles,
                    "total_results": data.get("totalResults", 0),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "symbol": symbol,
                    "error": data.get("message", "Failed to fetch news"),
                    "articles": []
                }
                
        except Exception as e:
            return {
                "symbol": symbol,
                "error": str(e),
                "articles": [],
                "timestamp": datetime.now().isoformat()
            }

class FREDAPITool(BaseTool):
    """Tool for fetching economic data from FRED (Federal Reserve Economic Data)"""
    
    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY")
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
    
    async def fetch_data(self, series_id: str = "GDP", **kwargs) -> Dict[str, Any]:
        """Fetch economic indicators from FRED"""
        if not self.api_key:
            return {"error": "FRED_API_KEY not configured", "data": []}
        
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": 100,
                "sort_order": "desc"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
            
            observations = data.get("observations", [])
            
            return {
                "series_id": series_id,
                "data": observations[:20],  # Latest 20 observations
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "series_id": series_id,
                "error": str(e),
                "data": [],
                "timestamp": datetime.now().isoformat()
            }

class AlphaVantageTool(BaseTool):
    """Tool for fetching data from Alpha Vantage API"""
    
    def __init__(self):
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    async def fetch_data(self, symbol: str, function: str = "OVERVIEW", **kwargs) -> Dict[str, Any]:
        """Fetch data from Alpha Vantage API"""
        if not self.api_key:
            return {"error": "ALPHA_VANTAGE_API_KEY not configured"}
        
        try:
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
            
            return {
                "symbol": symbol,
                "function": function,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "symbol": symbol,
                "function": function,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

class FinancialToolsManager:
    """Manager class to coordinate all financial data tools"""
    
    def __init__(self):
        self.yahoo_tool = YahooFinanceTool()
        self.news_tool = NewsAPITool()
        self.fred_tool = FREDAPITool()
        self.alphavantage_tool = AlphaVantageTool()
    
    async def get_comprehensive_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch comprehensive financial data from all available sources"""
        
        # Run all data fetching operations concurrently
        tasks = [
            self.yahoo_tool.fetch_data(symbol),
            self.news_tool.fetch_data(symbol),
            self.alphavantage_tool.fetch_data(symbol, "OVERVIEW"),
            self.fred_tool.fetch_data("GDP"),  # General economic indicator
            self.fred_tool.fetch_data("UNRATE"),  # Unemployment rate
            self.fred_tool.fetch_data("FEDFUNDS"),  # Federal funds rate
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "symbol": symbol,
            "yahoo_finance": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "news_data": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "alpha_vantage": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
            "economic_indicators": {
                "gdp": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
                "unemployment": results[4] if not isinstance(results[4], Exception) else {"error": str(results[4])},
                "fed_funds": results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])},
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_stock_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental analysis data for a stock"""
        return await self.yahoo_tool.fetch_data(symbol)
    
    async def get_market_news(self, symbol: str) -> Dict[str, Any]:
        """Get latest news for a stock"""
        return await self.news_tool.fetch_data(symbol)
    
    async def get_economic_context(self) -> Dict[str, Any]:
        """Get economic indicators for market context"""
        gdp_task = self.fred_tool.fetch_data("GDP")
        unemployment_task = self.fred_tool.fetch_data("UNRATE")
        fed_funds_task = self.fred_tool.fetch_data("FEDFUNDS")
        
        gdp_data, unemployment_data, fed_funds_data = await asyncio.gather(
            gdp_task, unemployment_task, fed_funds_task
        )
        
        return {
            "gdp": gdp_data,
            "unemployment": unemployment_data,
            "federal_funds_rate": fed_funds_data,
            "timestamp": datetime.now().isoformat()
        }

# Example usage
async def main():
    tools = FinancialToolsManager()
    data = await tools.get_comprehensive_data("AAPL")
    print(f"Fetched data for {data['symbol']}")
    print(f"Yahoo Finance status: {'success' if 'error' not in data['yahoo_finance'] else 'error'}")
    print(f"News articles: {len(data.get('news_data', {}).get('articles', []))}")

if __name__ == "__main__":
    asyncio.run(main())