# src/agents/research_agent.py
from smolagents import CodeAgent, Tool
from src.utils.config import FinancialAgentConfig
from src.utils.memory_manager import MemoryManager
from src.tools.data_fetchers import FinancialDataFetcher
from typing import Dict, List
import json

class InvestmentResearchAgent:
    def __init__(self):
        self.config = FinancialAgentConfig()
        self.model = self.config.get_model()
        self.memory = MemoryManager()
        self.data_fetcher = FinancialDataFetcher()
        
        # Define tools
        self.tools = [
            Tool.from_function(
                self.get_stock_analysis,
                name="get_stock_analysis",
                description="Comprehensive stock analysis using multiple data sources"
            ),
            Tool.from_function(
                self.plan_research_steps,
                name="plan_research_steps",
                description="Plan research steps for a given stock symbol"
            ),
            Tool.from_function(
                self.self_reflect,
                name="self_reflect",
                description="Evaluate the quality of analysis and suggest improvements"
            )
        ]
        
        self.agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            add_base_tools=True
        )
    
    def plan_research_steps(self, symbol: str) -> Dict:
        """Plan research steps for a given stock symbol"""
        plan = {
            'symbol': symbol,
            'steps': [
                'Fetch basic stock information and price history',
                'Analyze financial metrics and ratios',
                'Research company news and market sentiment',
                'Compare with industry peers',
                'Generate investment recommendation',
                'Self-reflect on analysis quality'
            ],
            'expected_outputs': [
                'Company overview and current valuation',
                'Financial health assessment',
                'Market sentiment analysis',
                'Competitive positioning',
                'Risk assessment and recommendation'
            ]
        }
        
        # Save plan to memory
        self.memory.save_memory(f'research_plan_{symbol}', plan)
        return plan
    
    def get_stock_analysis(self, symbol: str) -> Dict:
        """Comprehensive stock analysis"""
        # Fetch data
        stock_data = self.data_fetcher.get_stock_data(symbol)
        
        if 'error' in stock_data:
            return {'error': stock_data['error']}
        
        # Analyze data (this would be enhanced with LLM analysis)
        analysis = {
            'symbol': symbol,
            'company_name': stock_data.get('company_name'),
            'current_analysis': {
                'price': stock_data.get('current_price'),
                'market_cap': stock_data.get('market_cap'),
                'pe_ratio': stock_data.get('pe_ratio'),
                'sector': stock_data.get('sector')
            },
            'financial_health': self._assess_financial_health(stock_data),
            'recommendation': self._generate_recommendation(stock_data)
        }
        
        # Save to memory for learning
        self.memory.save_memory(f'analysis_{symbol}', analysis)
        return analysis
    
    def _assess_financial_health(self, stock_data: Dict) -> Dict:
        """Assess company financial health"""
        financials = stock_data.get('financials', {})
        
        return {
            'profit_margin': financials.get('profit_margin'),
            'debt_ratio': financials.get('debt_to_equity'),
            'revenue_growth': 'stable',  # Simplified
            'overall_health': 'good' if financials.get('profit_margin', 0) > 0.1 else 'caution'
        }
    
    def _generate_recommendation(self, stock_data: Dict) -> Dict:
        """Generate investment recommendation"""
        pe_ratio = stock_data.get('pe_ratio')
        
        if pe_ratio and pe_ratio < 15:
            rating = 'BUY'
        elif pe_ratio and pe_ratio < 25:
            rating = 'HOLD'
        else:
            rating = 'SELL'
            
        return {
            'rating': rating,
            'confidence': 0.8,
            'reasoning': f"Based on P/E ratio of {pe_ratio} and financial health"
        }
    
    def self_reflect(self, analysis: Dict) -> Dict:
        """Self-reflect on analysis quality"""
        reflection = {
            'quality_assessment': {
                'data_completeness': 'high',
                'analysis_depth': 'medium',
                'recommendation_clarity': 'high'
            },
            'improvement_suggestions': [
                'Incorporate more historical data',
                'Add peer comparison analysis',
                'Include macroeconomic factors'
            ],
            'learning_notes': 'Need to enhance news sentiment integration'
        }
        
        # Save reflection for future improvement
        self.memory.save_memory('reflection', reflection)
        return reflection
    
    def run_research(self, symbol: str) -> Dict:
        """Execute complete research workflow"""
        # Plan research
        plan = self.plan_research_steps(symbol)
        
        # Execute analysis
        analysis = self.get_stock_analysis(symbol)
        
        # Self-reflect
        reflection = self.self_reflect(analysis)
        
        return {
            'research_plan': plan,
            'analysis': analysis,
            'reflection': reflection,
            'memory_key': f'research_{symbol}_{self.memory.memories.get("timestamp")}'
        }