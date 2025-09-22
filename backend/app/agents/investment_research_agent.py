from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import asyncio
from datetime import datetime
import os

class AgentState(TypedDict):
    """State for the Investment Research Agent"""
    stock_symbol: str
    research_plan: List[str]
    collected_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    quality_assessment: Dict[str, Any]
    final_report: str
    memory_notes: List[str]
    iteration_count: int
    max_iterations: int

class InvestmentResearchAgent:
    """
    Autonomous Investment Research Agent that:
    - Plans its research steps for a given stock symbol
    - Uses tools dynamically (APIs, datasets, retrieval)
    - Self-reflects to assess the quality of its output
    - Learns across runs (keeps brief memories or notes to improve future analyses)
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for the research agent"""
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._plan_research)
        workflow.add_node("data_collector", self._collect_data)
        workflow.add_node("analyzer", self._analyze_data)
        workflow.add_node("quality_assessor", self._assess_quality)
        workflow.add_node("reporter", self._generate_report)
        workflow.add_node("memory_updater", self._update_memory)
        
        # Add edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "data_collector")
        workflow.add_edge("data_collector", "analyzer")
        workflow.add_edge("analyzer", "quality_assessor")
        
        # Conditional edge for quality assessment
        workflow.add_conditional_edges(
            "quality_assessor",
            self._should_refine,
            {
                "refine": "data_collector",  # Go back to collect more data
                "proceed": "reporter"        # Proceed to generate report
            }
        )
        
        workflow.add_edge("reporter", "memory_updater")
        workflow.add_edge("memory_updater", END)
        
        return workflow.compile()
    
    async def _plan_research(self, state: AgentState) -> AgentState:
        """Plan the research steps for the given stock symbol"""
        
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial research planner. Given a stock symbol, 
            create a comprehensive research plan that covers all important aspects of investment analysis.
            
            Consider these areas:
            1. Company fundamentals (financials, ratios, growth)
            2. Market sentiment and news analysis
            3. Technical analysis and price trends
            4. Industry and sector analysis
            5. Risk assessment and competitive analysis
            
            Return a structured list of specific research steps."""),
            ("human", f"Create a research plan for stock symbol: {state['stock_symbol']}")
        ])
        
        messages = planning_prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        
        # Parse the research plan
        research_plan = self._parse_research_plan(response.content)
        
        state["research_plan"] = research_plan
        state["iteration_count"] = 0
        state["max_iterations"] = 3
        
        return state
    
    async def _collect_data(self, state: AgentState) -> AgentState:
        """Collect data based on the research plan"""
        
        collected_data = {}
        
        # For now, we'll simulate data collection
        # In the actual implementation, this would call various APIs and tools
        
        # Simulate financial data collection
        collected_data["financial_metrics"] = {
            "pe_ratio": "Placeholder - would fetch from Yahoo Finance",
            "revenue_growth": "Placeholder - would calculate from historical data",
            "debt_to_equity": "Placeholder - would fetch from financial statements"
        }
        
        # Simulate news data collection
        collected_data["news_sentiment"] = {
            "recent_news": "Placeholder - would fetch from NewsAPI",
            "sentiment_score": "Placeholder - would analyze news sentiment",
            "key_topics": "Placeholder - would extract key themes"
        }
        
        # Simulate technical analysis data
        collected_data["technical_analysis"] = {
            "price_trend": "Placeholder - would analyze price charts",
            "support_resistance": "Placeholder - would identify key levels",
            "indicators": "Placeholder - would calculate technical indicators"
        }
        
        state["collected_data"] = collected_data
        return state
    
    async def _analyze_data(self, state: AgentState) -> AgentState:
        """Analyze the collected data and generate insights"""
        
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial analyst. Analyze the provided data 
            and generate comprehensive insights about the investment opportunity.
            
            Provide:
            1. Key financial highlights
            2. Investment thesis (bull and bear cases)
            3. Risk factors
            4. Valuation assessment
            5. Recommendation with reasoning"""),
            ("human", f"""Analyze this data for {state['stock_symbol']}:
            
            Research Plan: {state['research_plan']}
            Collected Data: {json.dumps(state['collected_data'], indent=2)}
            
            Provide a thorough analysis.""")
        ])
        
        messages = analysis_prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        
        analysis_results = {
            "analysis_text": response.content,
            "timestamp": datetime.now().isoformat(),
            "analyst": "Investment Research Agent"
        }
        
        state["analysis_results"] = analysis_results
        return state
    
    async def _assess_quality(self, state: AgentState) -> AgentState:
        """Self-reflect to assess the quality of the analysis"""
        
        quality_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a quality assessor for financial research. Evaluate the 
            completeness and quality of the analysis provided.
            
            Rate on a scale of 1-10 and provide specific feedback on:
            1. Data completeness (are key data points missing?)
            2. Analysis depth (is the analysis thorough?)
            3. Risk assessment (are risks properly identified?)
            4. Actionability (are recommendations clear and actionable?)
            
            If score is below 7, suggest specific improvements."""),
            ("human", f"""Assess this analysis for {state['stock_symbol']}:
            
            Analysis: {state['analysis_results']['analysis_text']}
            Available Data: {list(state['collected_data'].keys())}
            
            Provide quality score and feedback.""")
        ])
        
        messages = quality_prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        
        quality_assessment = {
            "assessment_text": response.content,
            "timestamp": datetime.now().isoformat(),
            "iteration": state["iteration_count"]
        }
        
        state["quality_assessment"] = quality_assessment
        state["iteration_count"] += 1
        
        return state
    
    def _should_refine(self, state: AgentState) -> str:
        """Decide whether to refine the analysis or proceed to reporting"""
        
        # Extract quality score from assessment (simplified logic)
        assessment_text = state["quality_assessment"]["assessment_text"].lower()
        
        # Check for quality indicators
        if state["iteration_count"] >= state["max_iterations"]:
            return "proceed"
        
        # Look for quality indicators in the assessment
        if any(phrase in assessment_text for phrase in ["below 7", "insufficient", "incomplete", "needs improvement"]):
            return "refine"
        
        return "proceed"
    
    async def _generate_report(self, state: AgentState) -> AgentState:
        """Generate the final investment research report"""
        
        report_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a senior financial analyst generating a comprehensive 
            investment research report. Create a professional, well-structured report 
            that investors can use to make informed decisions.
            
            Structure:
            1. Executive Summary
            2. Company Overview
            3. Financial Analysis
            4. Investment Thesis
            5. Risk Factors
            6. Valuation & Recommendation
            7. Conclusion"""),
            ("human", f"""Generate a comprehensive investment research report for {state['stock_symbol']}:
            
            Research Plan: {state['research_plan']}
            Analysis: {state['analysis_results']['analysis_text']}
            Quality Assessment: {state['quality_assessment']['assessment_text']}
            
            Create a professional investment research report.""")
        ])
        
        messages = report_prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        
        state["final_report"] = response.content
        return state
    
    async def _update_memory(self, state: AgentState) -> AgentState:
        """Update agent memory with learnings from this analysis"""
        
        memory_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract key learnings and insights from this research session 
            that could improve future analyses. Focus on:
            1. What worked well in the research approach
            2. What data sources were most valuable
            3. What analysis techniques provided best insights
            4. What could be improved for next time
            
            Keep notes concise but actionable."""),
            ("human", f"""Extract learnings from this research session for {state['stock_symbol']}:
            
            Quality Assessments: {state['quality_assessment']}
            Final Report Quality: Based on {state['iteration_count']} iterations
            
            What can be learned for future research?""")
        ])
        
        messages = memory_prompt.format_messages()
        response = await self.llm.ainvoke(messages)
        
        # Add to memory notes
        if "memory_notes" not in state:
            state["memory_notes"] = []
        
        state["memory_notes"].append({
            "timestamp": datetime.now().isoformat(),
            "stock_symbol": state["stock_symbol"],
            "learnings": response.content
        })
        
        return state
    
    def _parse_research_plan(self, plan_text: str) -> List[str]:
        """Parse the research plan from LLM response"""
        # Simple parsing logic - in practice, you'd want more sophisticated parsing
        lines = plan_text.split('\n')
        plan_steps = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                # Remove bullet points and numbering
                clean_step = line.lstrip('-*0123456789. ').strip()
                if clean_step:
                    plan_steps.append(clean_step)
        
        return plan_steps if plan_steps else ["Analyze company fundamentals", "Review recent news", "Assess market trends"]
    
    async def research_stock(self, stock_symbol: str) -> Dict[str, Any]:
        """Main method to research a stock symbol"""
        
        initial_state = AgentState(
            stock_symbol=stock_symbol,
            research_plan=[],
            collected_data={},
            analysis_results={},
            quality_assessment={},
            final_report="",
            memory_notes=[],
            iteration_count=0,
            max_iterations=3
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "stock_symbol": final_state["stock_symbol"],
            "research_plan": final_state["research_plan"],
            "final_report": final_state["final_report"],
            "quality_assessment": final_state["quality_assessment"],
            "memory_notes": final_state["memory_notes"],
            "iterations": final_state["iteration_count"]
        }

# Example usage
async def main():
    agent = InvestmentResearchAgent()
    result = await agent.research_stock("AAPL")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())