from typing import Dict, Any, List, Optional, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
import json
import asyncio
from datetime import datetime
from enum import Enum
import re
import os

class QualityMetric(Enum):
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    ACTIONABILITY = "actionability"
    CLARITY = "clarity"
    TIMELINESS = "timeliness"
    RISK_ASSESSMENT = "risk_assessment"
    DATA_QUALITY = "data_quality"

class EvaluationCriteria:
    """Defines evaluation criteria for financial analysis quality"""
    
    CRITERIA = {
        QualityMetric.ACCURACY: {
            "description": "Factual correctness and precision of data and analysis",
            "weight": 0.20,
            "benchmarks": {
                "excellent": "All facts verified, calculations correct, no material errors",
                "good": "Minor factual issues, calculations mostly correct",
                "fair": "Some factual errors, calculation mistakes present",
                "poor": "Significant factual errors, unreliable calculations"
            }
        },
        QualityMetric.COMPLETENESS: {
            "description": "Coverage of all relevant aspects and thoroughness",
            "weight": 0.15,
            "benchmarks": {
                "excellent": "Comprehensive coverage, all key aspects addressed",
                "good": "Most aspects covered, minimal gaps",
                "fair": "Some important aspects missing",
                "poor": "Significant gaps in analysis"
            }
        },
        QualityMetric.RELEVANCE: {
            "description": "Pertinence to investment decision-making",
            "weight": 0.15,
            "benchmarks": {
                "excellent": "Highly relevant insights for investment decisions",
                "good": "Mostly relevant with some tangential content",
                "fair": "Some relevance but includes unnecessary information",
                "poor": "Low relevance to investment decisions"
            }
        },
        QualityMetric.ACTIONABILITY: {
            "description": "Clear, implementable recommendations and insights",
            "weight": 0.15,
            "benchmarks": {
                "excellent": "Clear, specific, implementable recommendations",
                "good": "Generally actionable with minor ambiguity",
                "fair": "Some actionable elements but lacks specificity",
                "poor": "Vague, difficult to implement recommendations"
            }
        },
        QualityMetric.CLARITY: {
            "description": "Clear communication and logical structure",
            "weight": 0.10,
            "benchmarks": {
                "excellent": "Crystal clear, well-structured, easy to understand",
                "good": "Generally clear with minor confusion points",
                "fair": "Somewhat unclear, structure issues",
                "poor": "Confusing, poorly structured"
            }
        },
        QualityMetric.TIMELINESS: {
            "description": "Relevance to current market conditions and timing",
            "weight": 0.10,
            "benchmarks": {
                "excellent": "Highly current, considers latest market conditions",
                "good": "Mostly current with minor outdated elements",
                "fair": "Some outdated information or analysis",
                "poor": "Significantly outdated or irrelevant timing"
            }
        },
        QualityMetric.RISK_ASSESSMENT: {
            "description": "Thorough identification and analysis of risks",
            "weight": 0.10,
            "benchmarks": {
                "excellent": "Comprehensive risk identification and mitigation strategies",
                "good": "Good risk coverage with minor gaps",
                "fair": "Some risks identified but incomplete analysis",
                "poor": "Poor or missing risk assessment"
            }
        },
        QualityMetric.DATA_QUALITY: {
            "description": "Quality and reliability of underlying data sources",
            "weight": 0.05,
            "benchmarks": {
                "excellent": "High-quality, verified, authoritative sources",
                "good": "Generally reliable sources with minor concerns",
                "fair": "Mixed quality sources, some reliability issues",
                "poor": "Poor quality or unreliable data sources"
            }
        }
    }

class QualityEvaluator:
    """Evaluates the quality of financial analysis using multiple criteria"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.criteria = EvaluationCriteria.CRITERIA
    
    async def evaluate_analysis(self, analysis: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive evaluation of analysis quality"""
        
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a senior financial analysis quality evaluator. Evaluate the provided analysis 
            against these specific criteria:

            {self._format_criteria_for_prompt()}

            For each criterion, provide:
            1. Score (1-10 scale where 10 is excellent)
            2. Rating (poor/fair/good/excellent)
            3. Specific feedback explaining the score
            4. Suggestions for improvement

            Return evaluation in this JSON format:
            {{
                "overall_score": 8.5,
                "overall_rating": "good",
                "criteria_scores": {{
                    "accuracy": {{"score": 9, "rating": "excellent", "feedback": "...", "improvements": ["..."]}},
                    "completeness": {{"score": 7, "rating": "good", "feedback": "...", "improvements": ["..."]}},
                    ...
                }},
                "weighted_score": 8.2,
                "strengths": ["strength1", "strength2"],
                "weaknesses": ["weakness1", "weakness2"],
                "priority_improvements": ["improvement1", "improvement2"],
                "recommendation": "approve|revise|reject"
            }}"""),
            ("human", f"""Evaluate this financial analysis:

            Analysis: {json.dumps(analysis)}
            Context: {json.dumps(context) if context else 'No additional context provided'}

            Provide comprehensive quality evaluation.""")
        ])
        
        response = await self.llm.ainvoke(evaluation_prompt.format_messages())
        
        try:
            evaluation_result = json.loads(response.content)
            evaluation_result["evaluated_at"] = datetime.now().isoformat()
            evaluation_result["evaluator"] = "QualityEvaluator"
            return evaluation_result
        except json.JSONDecodeError:
            return self._create_fallback_evaluation(analysis, response.content)
    
    def _format_criteria_for_prompt(self) -> str:
        """Format evaluation criteria for the prompt"""
        formatted = []
        for metric, details in self.criteria.items():
            formatted.append(f"""
            {metric.value.upper()} (Weight: {details['weight']*100}%)
            - Description: {details['description']}
            - Excellent: {details['benchmarks']['excellent']}
            - Good: {details['benchmarks']['good']}
            - Fair: {details['benchmarks']['fair']}
            - Poor: {details['benchmarks']['poor']}
            """)
        return "\n".join(formatted)
    
    def _create_fallback_evaluation(self, analysis: Dict[str, Any], raw_response: str) -> Dict[str, Any]:
        """Create fallback evaluation when JSON parsing fails"""
        return {
            "overall_score": 6.0,
            "overall_rating": "fair",
            "error": "Failed to parse evaluation response",
            "raw_response": raw_response,
            "evaluated_at": datetime.now().isoformat(),
            "evaluator": "QualityEvaluator (fallback)"
        }

class AnalysisOptimizer:
    """Optimizes analysis based on evaluation feedback"""
    
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.2,  # Slightly higher for creative improvements
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    async def optimize_analysis(self, 
                              original_analysis: Dict[str, Any], 
                              evaluation: Dict[str, Any],
                              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Optimize analysis based on evaluation feedback"""
        
        optimization_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert financial analysis optimizer. Your job is to improve 
            the analysis based on the quality evaluation feedback provided.

            Focus on:
            1. Addressing specific weaknesses identified in the evaluation
            2. Enhancing strengths while maintaining quality
            3. Implementing priority improvements
            4. Ensuring the optimized analysis meets high standards

            Guidelines:
            - Maintain factual accuracy and data integrity
            - Improve clarity and actionability
            - Add missing elements for completeness
            - Enhance risk assessment if needed
            - Provide more specific and implementable recommendations
            - Ensure logical flow and structure

            Return the optimized analysis maintaining the original structure but with improvements."""),
            ("human", f"""Optimize this financial analysis:

            Original Analysis: {json.dumps(original_analysis)}
            
            Quality Evaluation: {json.dumps(evaluation)}
            
            Context: {json.dumps(context) if context else 'No additional context'}

            Provide an improved version addressing the evaluation feedback.""")
        ])
        
        response = await self.llm.ainvoke(optimization_prompt.format_messages())
        
        return {
            "optimized_analysis": response.content,
            "optimization_applied": True,
            "based_on_evaluation": evaluation.get("overall_score", 0),
            "addressed_weaknesses": evaluation.get("weaknesses", []),
            "implemented_improvements": evaluation.get("priority_improvements", []),
            "optimized_at": datetime.now().isoformat(),
            "optimizer": "AnalysisOptimizer"
        }

class EvaluatorOptimizerWorkflow:
    """
    Workflow that implements the Evaluator-Optimizer pattern:
    Generate analysis → evaluate quality → refine using feedback
    """
    
    def __init__(self, max_iterations: int = 3, min_quality_threshold: float = 7.0):
        self.evaluator = QualityEvaluator()
        self.optimizer = AnalysisOptimizer()
        self.max_iterations = max_iterations
        self.min_quality_threshold = min_quality_threshold
    
    async def process_with_evaluation(self, 
                                    analysis: Dict[str, Any], 
                                    context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main workflow method that evaluates and optimizes analysis iteratively
        """
        
        workflow_history = []
        current_analysis = analysis.copy()
        
        for iteration in range(self.max_iterations):
            print(f"🔄 Iteration {iteration + 1}/{self.max_iterations}")
            
            # Step 1: Evaluate current analysis
            print("📊 Evaluating analysis quality...")
            evaluation = await self.evaluator.evaluate_analysis(current_analysis, context)
            
            current_score = evaluation.get("overall_score", 0)
            print(f"📈 Quality Score: {current_score}/10 ({evaluation.get('overall_rating', 'unknown')})")
            
            # Record iteration
            iteration_record = {
                "iteration": iteration + 1,
                "analysis": current_analysis,
                "evaluation": evaluation,
                "quality_score": current_score,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 2: Check if quality threshold is met
            if current_score >= self.min_quality_threshold:
                print(f"✅ Quality threshold met! Score: {current_score}")
                iteration_record["optimization"] = None
                iteration_record["threshold_met"] = True
                workflow_history.append(iteration_record)
                break
            
            # Step 3: Optimize if threshold not met and not final iteration
            if iteration < self.max_iterations - 1:
                print("🔧 Optimizing analysis based on feedback...")
                optimization = await self.optimizer.optimize_analysis(
                    current_analysis, evaluation, context
                )
                
                # Update current analysis for next iteration
                try:
                    # Try to parse optimized analysis as JSON if it's structured
                    if optimization["optimized_analysis"].strip().startswith("{"):
                        current_analysis = json.loads(optimization["optimized_analysis"])
                    else:
                        # If it's text, update the analysis text field
                        if isinstance(current_analysis, dict) and "analysis" in current_analysis:
                            current_analysis["analysis"] = optimization["optimized_analysis"]
                        else:
                            current_analysis = {"analysis": optimization["optimized_analysis"]}
                except (json.JSONDecodeError, KeyError):
                    # Fallback: treat as text update
                    if isinstance(current_analysis, dict) and "analysis" in current_analysis:
                        current_analysis["analysis"] = optimization["optimized_analysis"]
                    else:
                        current_analysis = {"analysis": optimization["optimized_analysis"]}
                
                iteration_record["optimization"] = optimization
                iteration_record["threshold_met"] = False
                print(f"🔄 Analysis optimized for iteration {iteration + 2}")
            else:
                print("⚠️  Max iterations reached")
                iteration_record["optimization"] = None
                iteration_record["threshold_met"] = False
            
            workflow_history.append(iteration_record)
        
        # Generate final workflow summary
        final_evaluation = workflow_history[-1]["evaluation"]
        
        return {
            "success": True,
            "final_analysis": current_analysis,
            "final_evaluation": final_evaluation,
            "final_score": final_evaluation.get("overall_score", 0),
            "iterations_performed": len(workflow_history),
            "quality_threshold_met": final_evaluation.get("overall_score", 0) >= self.min_quality_threshold,
            "workflow_history": workflow_history,
            "improvements_made": [
                record["optimization"]["addressed_weaknesses"]
                for record in workflow_history
                if record.get("optimization")
            ],
            "workflow_summary": {
                "initial_score": workflow_history[0]["quality_score"],
                "final_score": final_evaluation.get("overall_score", 0),
                "improvement": final_evaluation.get("overall_score", 0) - workflow_history[0]["quality_score"],
                "threshold": self.min_quality_threshold,
                "max_iterations": self.max_iterations
            },
            "processed_at": datetime.now().isoformat(),
            "workflow": "evaluator_optimizer"
        }
    
    async def batch_process(self, 
                          analyses: List[Dict[str, Any]], 
                          context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Process multiple analyses with evaluation and optimization"""
        
        tasks = [self.process_with_evaluation(analysis, context) for analysis in analyses]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) else {"error": str(result)} for result in results]
    
    def get_quality_statistics(self, workflow_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate quality statistics from workflow results"""
        
        if not workflow_results:
            return {"error": "No results to analyze"}
        
        successful_results = [r for r in workflow_results if r.get("success")]
        
        if not successful_results:
            return {"error": "No successful results to analyze"}
        
        initial_scores = [r["workflow_summary"]["initial_score"] for r in successful_results]
        final_scores = [r["workflow_summary"]["final_score"] for r in successful_results]
        improvements = [r["workflow_summary"]["improvement"] for r in successful_results]
        
        return {
            "total_analyses": len(workflow_results),
            "successful_analyses": len(successful_results),
            "average_initial_score": sum(initial_scores) / len(initial_scores),
            "average_final_score": sum(final_scores) / len(final_scores),
            "average_improvement": sum(improvements) / len(improvements),
            "threshold_met_count": sum(1 for r in successful_results if r["quality_threshold_met"]),
            "threshold_met_percentage": (sum(1 for r in successful_results if r["quality_threshold_met"]) / len(successful_results)) * 100,
            "max_improvement": max(improvements) if improvements else 0,
            "min_improvement": min(improvements) if improvements else 0
        }

# Example usage
async def main():
    # Sample analysis to be evaluated and optimized
    sample_analysis = {
        "symbol": "AAPL",
        "analysis": """Apple Inc. is doing well. The stock price went up. 
        Revenue increased. Profit margins are good. Recommend buying.""",
        "recommendation": "BUY",
        "analyst": "Sample Analyst"
    }
    
    workflow = EvaluatorOptimizerWorkflow(max_iterations=3, min_quality_threshold=8.0)
    result = await workflow.process_with_evaluation(sample_analysis)
    
    if result["success"]:
        print(f"Final Score: {result['final_score']}/10")
        print(f"Improvements: {result['workflow_summary']['improvement']:.1f} points")
        print(f"Threshold Met: {result['quality_threshold_met']}")
        print(f"Iterations: {result['iterations_performed']}")
    else:
        print(f"Workflow failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())