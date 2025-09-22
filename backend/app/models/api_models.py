from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

# Request Models
class StockAnalysisRequest(BaseModel):
    """Request model for stock analysis"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, MSFT)")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis: comprehensive, basic, technical")
    include_news: bool = Field(default=True, description="Include news analysis")
    include_financials: bool = Field(default=True, description="Include financial data")
    time_horizon: str = Field(default="1y", description="Analysis time horizon")

class NewsProcessingRequest(BaseModel):
    """Request model for news processing"""
    news_articles: List[Dict[str, Any]] = Field(..., description="List of news articles to process")
    target_symbol: Optional[str] = Field(None, description="Target stock symbol for focused analysis")
    processing_type: str = Field(default="full_chain", description="Processing type: full_chain, classify_only, extract_only")

class ContentRoutingRequest(BaseModel):
    """Request model for content routing"""
    content: Dict[str, Any] = Field(..., description="Content to be routed to specialist")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for routing decision")

class AnalysisEvaluationRequest(BaseModel):
    """Request model for analysis evaluation"""
    analysis: Dict[str, Any] = Field(..., description="Analysis to be evaluated")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for evaluation")
    optimize: bool = Field(default=True, description="Whether to optimize based on evaluation")
    max_iterations: int = Field(default=3, description="Maximum optimization iterations")
    quality_threshold: float = Field(default=7.0, description="Minimum quality threshold")

# Response Models
class StockAnalysisResponse(BaseModel):
    """Response model for stock analysis"""
    success: bool
    symbol: str
    analysis: Dict[str, Any]
    research_plan: List[str]
    quality_assessment: Dict[str, Any]
    processing_time: float
    timestamp: datetime
    error: Optional[str] = None

class NewsProcessingResponse(BaseModel):
    """Response model for news processing"""
    success: bool
    processed_articles: int
    final_summary: str
    chain_results: Dict[str, Any]
    processing_time: float
    timestamp: datetime
    error: Optional[str] = None

class ContentRoutingResponse(BaseModel):
    """Response model for content routing"""
    success: bool
    routing_decision: Dict[str, Any]
    specialist_analysis: Dict[str, Any]
    confidence: float
    processing_time: float
    timestamp: datetime
    error: Optional[str] = None

class AnalysisEvaluationResponse(BaseModel):
    """Response model for analysis evaluation"""
    success: bool
    final_score: float
    final_analysis: Dict[str, Any]
    iterations_performed: int
    quality_threshold_met: bool
    workflow_summary: Dict[str, Any]
    processing_time: float
    timestamp: datetime
    error: Optional[str] = None

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime
    request_id: Optional[str] = None