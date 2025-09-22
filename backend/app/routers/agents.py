from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import time
from datetime import datetime
import asyncio

# Import our models
from app.models.api_models import (
    StockAnalysisRequest, 
    StockAnalysisResponse,
    ErrorResponse
)

# Import our agent and tools
try:
    from app.agents.investment_research_agent import InvestmentResearchAgent
    from app.tools.financial_tools import FinancialToolsManager
except ImportError as e:
    print(f"Warning: Could not import agents/tools: {e}")
    InvestmentResearchAgent = None
    FinancialToolsManager = None

router = APIRouter()

# Initialize components (with error handling for missing dependencies)
try:
    research_agent = InvestmentResearchAgent() if InvestmentResearchAgent else None
    tools_manager = FinancialToolsManager() if FinancialToolsManager else None
except Exception as e:
    print(f"Warning: Could not initialize components: {e}")
    research_agent = None
    tools_manager = None

@router.post("/research", response_model=StockAnalysisResponse)
async def research_stock(request: StockAnalysisRequest):
    """
    Comprehensive stock research using the Investment Research Agent
    """
    start_time = time.time()
    
    try:
        if not research_agent:
            raise HTTPException(
                status_code=503, 
                detail="Investment Research Agent not available"
            )
        
        # Perform stock research
        result = await research_agent.research_stock(request.symbol)
        
        processing_time = time.time() - start_time
        
        return StockAnalysisResponse(
            success=True,
            symbol=request.symbol,
            analysis=result,
            research_plan=result.get("research_plan", []),
            quality_assessment=result.get("quality_assessment", {}),
            processing_time=processing_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        return StockAnalysisResponse(
            success=False,
            symbol=request.symbol,
            analysis={},
            research_plan=[],
            quality_assessment={},
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=str(e)
        )

@router.get("/data/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get comprehensive financial data for a stock symbol
    """
    start_time = time.time()
    
    try:
        if not tools_manager:
            # Fallback to basic data if tools not available
            return {
                "symbol": symbol,
                "message": "Basic data only - full tools not available",
                "timestamp": datetime.now().isoformat(),
                "processing_time": time.time() - start_time
            }
        
        # Get comprehensive financial data
        data = await tools_manager.get_comprehensive_data(symbol)
        
        return {
            "success": True,
            "data": data,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/fundamentals/{symbol}")
async def get_stock_fundamentals(symbol: str):
    """
    Get fundamental analysis data for a stock
    """
    start_time = time.time()
    
    try:
        if not tools_manager:
            raise HTTPException(
                status_code=503,
                detail="Financial tools manager not available"
            )
        
        fundamentals = await tools_manager.get_stock_fundamentals(symbol)
        
        return {
            "success": True,
            "symbol": symbol,
            "fundamentals": fundamentals,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/news/{symbol}")
async def get_stock_news(symbol: str, limit: int = 20):
    """
    Get latest news for a stock symbol
    """
    start_time = time.time()
    
    try:
        if not tools_manager:
            raise HTTPException(
                status_code=503,
                detail="Financial tools manager not available"
            )
        
        news_data = await tools_manager.get_market_news(symbol)
        
        # Limit results if requested
        if "articles" in news_data and len(news_data["articles"]) > limit:
            news_data["articles"] = news_data["articles"][:limit]
        
        return {
            "success": True,
            "symbol": symbol,
            "news": news_data,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
        )

@router.get("/economic-context")
async def get_economic_context():
    """
    Get current economic indicators and context
    """
    start_time = time.time()
    
    try:
        if not tools_manager:
            raise HTTPException(
                status_code=503,
                detail="Financial tools manager not available"
            )
        
        economic_data = await tools_manager.get_economic_context()
        
        return {
            "success": True,
            "economic_data": economic_data,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
        )

@router.post("/batch-research")
async def batch_research_stocks(symbols: list[str], background_tasks: BackgroundTasks):
    """
    Research multiple stocks in batch (background processing)
    """
    
    if not research_agent:
        raise HTTPException(
            status_code=503,
            detail="Investment Research Agent not available"
        )
    
    if len(symbols) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 symbols allowed per batch request"
        )
    
    # Start background task
    task_id = f"batch_{int(time.time())}"
    
    async def process_batch():
        results = {}
        for symbol in symbols:
            try:
                result = await research_agent.research_stock(symbol)
                results[symbol] = {"success": True, "data": result}
            except Exception as e:
                results[symbol] = {"success": False, "error": str(e)}
        
        # In a real implementation, you'd store this in a database or cache
        print(f"Batch {task_id} completed: {results}")
        return results
    
    background_tasks.add_task(process_batch)
    
    return {
        "task_id": task_id,
        "status": "started",
        "symbols": symbols,
        "estimated_completion": "2-5 minutes",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the agents service
    """
    
    services_status = {
        "research_agent": "available" if research_agent else "unavailable",
        "tools_manager": "available" if tools_manager else "unavailable",
        "api_endpoints": "available"
    }
    
    overall_status = "healthy" if all(
        status == "available" for status in services_status.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": services_status
    }