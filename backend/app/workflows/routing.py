from typing import Dict, Any, List, Optional, Union
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from enum import Enum
import json
import asyncio
from datetime import datetime
import os

class ContentType(Enum):
    EARNINGS = "earnings"
    NEWS = "news"
    MARKET_DATA = "market_data"
    ANALYST_RATING = "analyst_rating"
    ECONOMIC_INDICATOR = "economic_indicator"
    TECHNICAL_ANALYSIS = "technical_analysis"
    UNKNOWN = "unknown"

class SpecialistType(Enum):
    EARNINGS_ANALYST = "earnings_analyst"
    NEWS_ANALYST = "news_analyst"
    MARKET_ANALYST = "market_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    ECONOMIC_ANALYST = "economic_analyst"
    GENERAL_ANALYST = "general_analyst"

class ContentRouter:
    """
    Router that determines the most appropriate specialist agent for content analysis
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def route_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Route content to the appropriate specialist"""
        
        routing_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a content router for financial analysis. Analyze the provided content 
            and determine which specialist should handle it. Consider:
            
            1. Content Type:
               - earnings: Financial reports, quarterly/annual results, revenue/profit data
               - news: Company news, announcements, press releases
               - market_data: Stock prices, trading volumes, market movements
               - analyst_rating: Research reports, price targets, recommendations
               - economic_indicator: GDP, inflation, employment data, central bank news
               - technical_analysis: Chart patterns, technical indicators, price trends
            
            2. Routing Decision Factors:
               - Primary focus of the content
               - Data type and structure
               - Analysis complexity required
               - Time sensitivity
               - Stakeholder impact
            
            Return your routing decision in this JSON format:
            {{
                "content_type": "earnings|news|market_data|analyst_rating|economic_indicator|technical_analysis",
                "specialist": "earnings_analyst|news_analyst|market_analyst|technical_analyst|economic_analyst|general_analyst",
                "confidence": 0.95,
                "reasoning": "Brief explanation of routing decision",
                "priority": "high|medium|low",
                "estimated_complexity": "simple|moderate|complex"
            }}"""),
            ("human", f"Route this content to the appropriate specialist: {json.dumps(content)}")
        ])
        
        response = await self.llm.ainvoke(routing_prompt.format_messages())
        
        try:
            routing_decision = json.loads(response.content)
            return routing_decision
        except json.JSONDecodeError:
            # Fallback routing
            return {
                "content_type": "unknown",
                "specialist": "general_analyst",
                "confidence": 0.5,
                "reasoning": "Failed to parse routing decision, using general analyst",
                "priority": "medium",
                "estimated_complexity": "moderate"
            }

class BaseSpecialistAgent:
    """Base class for all specialist agents"""
    
    def __init__(self, specialist_type: SpecialistType, llm_model: str = "gpt-4"):
        self.specialist_type = specialist_type
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def analyze(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Base analyze method to be overridden by specialists"""
        raise NotImplementedError("Subclasses must implement analyze method")

class EarningsSpecialist(BaseSpecialistAgent):
    """Specialist for analyzing earnings reports and financial statements"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(SpecialistType.EARNINGS_ANALYST, llm_model)
    
    async def analyze(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze earnings and financial data"""
        
        earnings_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert earnings analyst. Analyze financial reports, earnings data, 
            and company financial metrics. Focus on:
            
            1. Financial Performance:
               - Revenue growth and trends
               - Profit margins and profitability
               - Earnings per share (EPS) analysis
               - Cash flow evaluation
               - Balance sheet strength
            
            2. Key Metrics Analysis:
               - Year-over-year comparisons
               - Quarter-over-quarter trends
               - Guidance vs. actual performance
               - Beat/miss analysis
            
            3. Investment Implications:
               - Valuation impact
               - Growth prospects
               - Risk factors
               - Competitive positioning
            
            Provide detailed financial analysis with specific numbers and actionable insights."""),
            ("human", f"""Analyze this earnings/financial content:
            
            Content: {json.dumps(content)}
            Context: {json.dumps(context) if context else 'No additional context'}
            
            Provide comprehensive earnings analysis.""")
        ])
        
        response = await self.llm.ainvoke(earnings_prompt.format_messages())
        
        return {
            "specialist": "earnings_analyst",
            "analysis": response.content,
            "analysis_type": "financial_performance",
            "timestamp": datetime.now().isoformat(),
            "key_metrics_focus": ["revenue", "eps", "margins", "cash_flow"],
            "confidence": 0.9
        }

class NewsSpecialist(BaseSpecialistAgent):
    """Specialist for analyzing news and market sentiment"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(SpecialistType.NEWS_ANALYST, llm_model)
    
    async def analyze(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze news content and market sentiment"""
        
        news_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert news analyst specializing in financial market sentiment. 
            Analyze news content for:
            
            1. Sentiment Analysis:
               - Overall tone (positive/negative/neutral)
               - Market sentiment implications
               - Investor sentiment indicators
               - Public perception impact
            
            2. Market Impact Assessment:
               - Short-term price impact potential
               - Long-term strategic implications
               - Sector-wide effects
               - Competitive landscape changes
            
            3. Risk and Opportunity Identification:
               - Emerging risks from news
               - New opportunities highlighted
               - Regulatory implications
               - Stakeholder impacts
            
            Focus on actionable insights for investment decisions."""),
            ("human", f"""Analyze this news content:
            
            Content: {json.dumps(content)}
            Context: {json.dumps(context) if context else 'No additional context'}
            
            Provide comprehensive news sentiment and impact analysis.""")
        ])
        
        response = await self.llm.ainvoke(news_prompt.format_messages())
        
        return {
            "specialist": "news_analyst",
            "analysis": response.content,
            "analysis_type": "sentiment_and_impact",
            "timestamp": datetime.now().isoformat(),
            "focus_areas": ["sentiment", "market_impact", "risks", "opportunities"],
            "confidence": 0.85
        }

class MarketSpecialist(BaseSpecialistAgent):
    """Specialist for analyzing market data and trends"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(SpecialistType.MARKET_ANALYST, llm_model)
    
    async def analyze(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze market data and trading patterns"""
        
        market_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert market analyst specializing in market data interpretation. 
            Analyze market information for:
            
            1. Price Action Analysis:
               - Price trends and patterns
               - Volume analysis
               - Support and resistance levels
               - Momentum indicators
            
            2. Market Context:
               - Relative performance vs market/sector
               - Trading volume patterns
               - Market breadth indicators
               - Institutional activity signals
            
            3. Trading Implications:
               - Entry/exit points
               - Risk management levels
               - Position sizing considerations
               - Time horizon recommendations
            
            Provide data-driven market insights with specific levels and targets."""),
            ("human", f"""Analyze this market data:
            
            Content: {json.dumps(content)}
            Context: {json.dumps(context) if context else 'No additional context'}
            
            Provide comprehensive market analysis.""")
        ])
        
        response = await self.llm.ainvoke(market_prompt.format_messages())
        
        return {
            "specialist": "market_analyst",
            "analysis": response.content,
            "analysis_type": "market_data_analysis",
            "timestamp": datetime.now().isoformat(),
            "focus_areas": ["price_action", "volume", "trends", "levels"],
            "confidence": 0.88
        }

class TechnicalSpecialist(BaseSpecialistAgent):
    """Specialist for technical analysis"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(SpecialistType.TECHNICAL_ANALYST, llm_model)
    
    async def analyze(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze technical indicators and chart patterns"""
        
        technical_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical analyst. Analyze charts, patterns, and technical indicators:
            
            1. Chart Pattern Analysis:
               - Trend patterns (ascending, descending, sideways)
               - Reversal patterns (head and shoulders, double tops/bottoms)
               - Continuation patterns (flags, pennants, triangles)
               - Candlestick patterns
            
            2. Technical Indicators:
               - Moving averages and crossovers
               - RSI, MACD, Bollinger Bands
               - Support and resistance levels
               - Fibonacci retracements
            
            3. Trading Signals:
               - Buy/sell signals
               - Stop-loss levels
               - Price targets
               - Risk-reward ratios
            
            Provide specific technical levels and actionable trading insights."""),
            ("human", f"""Perform technical analysis on this data:
            
            Content: {json.dumps(content)}
            Context: {json.dumps(context) if context else 'No additional context'}
            
            Provide detailed technical analysis.""")
        ])
        
        response = await self.llm.ainvoke(technical_prompt.format_messages())
        
        return {
            "specialist": "technical_analyst",
            "analysis": response.content,
            "analysis_type": "technical_analysis",
            "timestamp": datetime.now().isoformat(),
            "focus_areas": ["patterns", "indicators", "levels", "signals"],
            "confidence": 0.82
        }

class EconomicSpecialist(BaseSpecialistAgent):
    """Specialist for economic indicators and macroeconomic analysis"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        super().__init__(SpecialistType.ECONOMIC_ANALYST, llm_model)
    
    async def analyze(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze economic indicators and macroeconomic trends"""
        
        economic_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert macroeconomic analyst. Analyze economic data and indicators:
            
            1. Economic Indicators Analysis:
               - GDP growth and trends
               - Inflation metrics (CPI, PPI)
               - Employment data
               - Interest rates and monetary policy
            
            2. Market Implications:
               - Sector rotation effects
               - Currency impacts
               - Bond market implications
               - Equity market effects
            
            3. Investment Strategy Impact:
               - Asset allocation implications
               - Geographic investment effects
               - Timing considerations
               - Risk management adjustments
            
            Connect economic data to investment opportunities and risks."""),
            ("human", f"""Analyze this economic data:
            
            Content: {json.dumps(content)}
            Context: {json.dumps(context) if context else 'No additional context'}
            
            Provide macroeconomic analysis and investment implications.""")
        ])
        
        response = await self.llm.ainvoke(economic_prompt.format_messages())
        
        return {
            "specialist": "economic_analyst",
            "analysis": response.content,
            "analysis_type": "macroeconomic_analysis",
            "timestamp": datetime.now().isoformat(),
            "focus_areas": ["indicators", "policy", "markets", "strategy"],
            "confidence": 0.87
        }

class RoutingWorkflow:
    """
    Main workflow that routes content to appropriate specialists and coordinates analysis
    """
    
    def __init__(self):
        self.router = ContentRouter()
        self.specialists = {
            SpecialistType.EARNINGS_ANALYST: EarningsSpecialist(),
            SpecialistType.NEWS_ANALYST: NewsSpecialist(),
            SpecialistType.MARKET_ANALYST: MarketSpecialist(),
            SpecialistType.TECHNICAL_ANALYST: TechnicalSpecialist(),
            SpecialistType.ECONOMIC_ANALYST: EconomicSpecialist(),
        }
    
    async def process_content(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main method to route and analyze content"""
        
        try:
            # Step 1: Route content to appropriate specialist
            print("🔄 Routing content to appropriate specialist...")
            routing_decision = await self.router.route_content(content)
            
            # Step 2: Get the appropriate specialist
            specialist_type_str = routing_decision.get("specialist", "general_analyst")
            
            # Map string to enum
            specialist_mapping = {
                "earnings_analyst": SpecialistType.EARNINGS_ANALYST,
                "news_analyst": SpecialistType.NEWS_ANALYST,
                "market_analyst": SpecialistType.MARKET_ANALYST,
                "technical_analyst": SpecialistType.TECHNICAL_ANALYST,
                "economic_analyst": SpecialistType.ECONOMIC_ANALYST,
            }
            
            specialist_type = specialist_mapping.get(specialist_type_str, SpecialistType.NEWS_ANALYST)
            specialist = self.specialists.get(specialist_type)
            
            if not specialist:
                print(f"❌ No specialist found for type: {specialist_type_str}")
                return {
                    "error": f"No specialist available for {specialist_type_str}",
                    "routing_decision": routing_decision
                }
            
            print(f"✅ Content routed to: {specialist_type_str}")
            
            # Step 3: Perform specialist analysis
            print("🔄 Performing specialist analysis...")
            analysis_result = await specialist.analyze(content, context)
            
            print("✅ Specialist analysis completed!")
            
            return {
                "success": True,
                "routing_decision": routing_decision,
                "specialist_analysis": analysis_result,
                "processed_at": datetime.now().isoformat(),
                "workflow": "routing_workflow"
            }
            
        except Exception as e:
            print(f"❌ Routing workflow failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    async def process_multiple_content(self, content_list: List[Dict[str, Any]], context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Process multiple pieces of content concurrently"""
        
        tasks = [self.process_content(content, context) for content in content_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) else {"error": str(result)} for result in results]

# Example usage
async def main():
    # Sample content for different specialists
    sample_contents = [
        {
            "type": "earnings_report",
            "data": {
                "company": "AAPL",
                "quarter": "Q3 2024",
                "revenue": "$50B",
                "eps": "$1.25",
                "guidance": "Strong outlook for Q4"
            }
        },
        {
            "type": "news_article",
            "data": {
                "title": "Federal Reserve Signals Rate Cut",
                "content": "The Federal Reserve indicated potential rate cuts...",
                "sentiment": "market_positive"
            }
        },
        {
            "type": "market_data",
            "data": {
                "symbol": "AAPL",
                "price": "$150.25",
                "volume": "50M",
                "change": "+2.5%"
            }
        }
    ]
    
    workflow = RoutingWorkflow()
    
    for content in sample_contents:
        result = await workflow.process_content(content)
        if result.get("success"):
            routing = result["routing_decision"]
            print(f"Content routed to: {routing['specialist']} (confidence: {routing['confidence']})")
            print(f"Reasoning: {routing['reasoning']}")
        else:
            print(f"Processing failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())