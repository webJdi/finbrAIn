from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import time
from datetime import datetime
import asyncio

# Import our models
from app.models.api_models import (
    NewsProcessingRequest,
    NewsProcessingResponse,
    ContentRoutingRequest,
    ContentRoutingResponse,
    AnalysisEvaluationRequest,
    AnalysisEvaluationResponse,
    ErrorResponse
)

# Import our workflows
try:
    from app.workflows.prompt_chaining import NewsProcessingChain
    from app.workflows.routing import RoutingWorkflow
    from app.workflows.evaluator_optimizer import EvaluatorOptimizerWorkflow
except ImportError as e:
    print(f"Warning: Could not import workflows: {e}")
    NewsProcessingChain = None
    RoutingWorkflow = None
    EvaluatorOptimizerWorkflow = None

router = APIRouter()

# Initialize workflow components
try:
    news_processor = NewsProcessingChain() if NewsProcessingChain else None
    routing_workflow = RoutingWorkflow() if RoutingWorkflow else None
    evaluator_optimizer = EvaluatorOptimizerWorkflow() if EvaluatorOptimizerWorkflow else None
except Exception as e:
    print(f"Warning: Could not initialize workflows: {e}")
    news_processor = None
    routing_workflow = None
    evaluator_optimizer = None

@router.post("/news/process", response_model=NewsProcessingResponse)
async def process_news(request: NewsProcessingRequest):
    """
    Process news articles through the prompt chaining workflow:
    Ingest → Preprocess → Classify → Extract → Summarize
    """
    start_time = time.time()
    
    try:
        if not news_processor:
            raise HTTPException(
                status_code=503,
                detail="News processing workflow not available"
            )
        
        # Process news through the chain
        result = await news_processor.process_news(request.news_articles)
        
        processing_time = time.time() - start_time
        
        return NewsProcessingResponse(
            success=result.get("success", False),
            processed_articles=len(request.news_articles),
            final_summary=result.get("final_summary", ""),
            chain_results=result.get("chain_results", {}),
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=result.get("error")
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        return NewsProcessingResponse(
            success=False,
            processed_articles=0,
            final_summary="",
            chain_results={},
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=str(e)
        )

@router.post("/content/route", response_model=ContentRoutingResponse)
async def route_content(request: ContentRoutingRequest):
    """
    Route content to the appropriate specialist agent
    """
    start_time = time.time()
    
    try:
        if not routing_workflow:
            raise HTTPException(
                status_code=503,
                detail="Content routing workflow not available"
            )
        
        # Route content to specialist
        result = await routing_workflow.process_content(
            request.content, 
            request.context
        )
        
        processing_time = time.time() - start_time
        
        return ContentRoutingResponse(
            success=result.get("success", False),
            routing_decision=result.get("routing_decision", {}),
            specialist_analysis=result.get("specialist_analysis", {}),
            confidence=result.get("routing_decision", {}).get("confidence", 0.0),
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=result.get("error")
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        return ContentRoutingResponse(
            success=False,
            routing_decision={},
            specialist_analysis={},
            confidence=0.0,
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=str(e)
        )

@router.post("/analysis/evaluate", response_model=AnalysisEvaluationResponse)
async def evaluate_analysis(request: AnalysisEvaluationRequest):
    """
    Evaluate and optimize analysis using the evaluator-optimizer workflow
    """
    start_time = time.time()
    
    try:
        if not evaluator_optimizer:
            raise HTTPException(
                status_code=503,
                detail="Analysis evaluation workflow not available"
            )
        
        # Configure the workflow with request parameters
        workflow = EvaluatorOptimizerWorkflow(
            max_iterations=request.max_iterations,
            min_quality_threshold=request.quality_threshold
        )
        
        if request.optimize:
            # Run full evaluation and optimization workflow
            result = await workflow.process_with_evaluation(
                request.analysis,
                request.context
            )
        else:
            # Run evaluation only
            evaluation = await workflow.evaluator.evaluate_analysis(
                request.analysis,
                request.context
            )
            result = {
                "success": True,
                "final_analysis": request.analysis,
                "final_evaluation": evaluation,
                "final_score": evaluation.get("overall_score", 0),
                "iterations_performed": 1,
                "quality_threshold_met": evaluation.get("overall_score", 0) >= request.quality_threshold,
                "workflow_summary": {
                    "initial_score": evaluation.get("overall_score", 0),
                    "final_score": evaluation.get("overall_score", 0),
                    "improvement": 0,
                    "threshold": request.quality_threshold,
                    "max_iterations": 1
                }
            }
        
        processing_time = time.time() - start_time
        
        return AnalysisEvaluationResponse(
            success=result.get("success", False),
            final_score=result.get("final_score", 0.0),
            final_analysis=result.get("final_analysis", {}),
            iterations_performed=result.get("iterations_performed", 0),
            quality_threshold_met=result.get("quality_threshold_met", False),
            workflow_summary=result.get("workflow_summary", {}),
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=result.get("error")
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        return AnalysisEvaluationResponse(
            success=False,
            final_score=0.0,
            final_analysis={},
            iterations_performed=0,
            quality_threshold_met=False,
            workflow_summary={},
            processing_time=processing_time,
            timestamp=datetime.now(),
            error=str(e)
        )

@router.post("/batch/route-content")
async def batch_route_content(content_list: List[Dict[str, Any]], context: Dict[str, Any] = None):
    """
    Route multiple content items to appropriate specialists
    """
    start_time = time.time()
    
    try:
        if not routing_workflow:
            raise HTTPException(
                status_code=503,
                detail="Content routing workflow not available"
            )
        
        if len(content_list) > 20:
            raise HTTPException(
                status_code=400,
                detail="Maximum 20 content items allowed per batch request"
            )
        
        # Process content items concurrently
        results = await routing_workflow.process_multiple_content(content_list, context)
        
        processing_time = time.time() - start_time
        
        return {
            "success": True,
            "processed_count": len(content_list),
            "results": results,
            "processing_time": processing_time,
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

@router.get("/workflows/status")
async def get_workflows_status():
    """
    Get the status of all available workflows
    """
    
    workflows_status = {
        "news_processing": {
            "available": news_processor is not None,
            "description": "News → Preprocess → Classify → Extract → Summarize",
            "endpoint": "/analysis/news/process"
        },
        "content_routing": {
            "available": routing_workflow is not None,
            "description": "Route content to specialist agents",
            "endpoint": "/analysis/content/route"
        },
        "evaluator_optimizer": {
            "available": evaluator_optimizer is not None,
            "description": "Evaluate and optimize analysis quality",
            "endpoint": "/analysis/analysis/evaluate"
        }
    }
    
    available_count = sum(1 for wf in workflows_status.values() if wf["available"])
    total_count = len(workflows_status)
    
    return {
        "status": "healthy" if available_count == total_count else "degraded",
        "available_workflows": available_count,
        "total_workflows": total_count,
        "workflows": workflows_status,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health_check():
    """
    Health check for the analysis workflows service
    """
    
    workflow_status = {
        "news_processor": "available" if news_processor else "unavailable",
        "routing_workflow": "available" if routing_workflow else "unavailable",
        "evaluator_optimizer": "available" if evaluator_optimizer else "unavailable"
    }
    
    overall_status = "healthy" if all(
        status == "available" for status in workflow_status.values()
    ) else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "workflows": workflow_status
    }