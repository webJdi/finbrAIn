# src/workflows/evaluator_optimizer.py
from typing import Dict, List
import json

class EvaluatorOptimizerWorkflow:
    """Implement Evaluator-Optimizer: Generate → evaluate → refine using feedback"""
    
    def __init__(self, model):
        self.model = model
        self.iteration_history = []
    
    def generate_analysis(self, symbol: str, data: Dict) -> Dict:
        """Generate initial analysis"""
        analysis = {
            'symbol': symbol,
            'initial_assessment': {
                'valuation': 'fair',
                'growth_prospects': 'moderate',
                'risk_level': 'medium'
            },
            'recommendation': 'HOLD',
            'reasoning': 'Based on current market data and financial metrics'
        }
        return analysis
    
    def evaluate_quality(self, analysis: Dict) -> Dict:
        """Evaluate analysis quality"""
        score = 0
        feedback = []
        
        if analysis.get('initial_assessment'):
            score += 25
        else:
            feedback.append("Missing initial assessment")
            
        if analysis.get('recommendation'):
            score += 25
        else:
            feedback.append("Missing clear recommendation")
            
        if analysis.get('reasoning'):
            score += 25
        else:
            feedback.append("Missing reasoning")
            
        if len(analysis) >= 3:
            score += 25
        else:
            feedback.append("Analysis lacks depth")
        
        return {
            'quality_score': score,
            'feedback_points': feedback,
            'grade': 'A' if score >= 80 else 'B' if score >= 60 else 'C'
        }
    
    def optimize_analysis(self, analysis: Dict, evaluation: Dict) -> Dict:
        """Refine analysis based on evaluation feedback"""
        optimized = analysis.copy()
        
        # Address feedback points
        for feedback in evaluation['feedback_points']:
            if "Missing initial assessment" in feedback:
                optimized['enhanced_assessment'] = {
                    **optimized.get('initial_assessment', {}),
                    'detailed_metrics': ['P/E ratio', 'P/B ratio', 'ROE']
                }
            elif "Missing reasoning" in feedback:
                optimized['detailed_reasoning'] = """
                Comprehensive analysis considering:
                - Financial ratios and metrics
                - Industry positioning
                - Market conditions
                - Risk factors
                """
        
        # Add optimization notes
        optimized['optimization_notes'] = {
            'original_score': evaluation['quality_score'],
            'improvements_made': evaluation['feedback_points'],
            'iterations': len(self.iteration_history) + 1
        }
        
        return optimized
    
    def execute_workflow(self, symbol: str, data: Dict) -> Dict:
        """Execute complete evaluator-optimizer workflow"""
        
        # Generate initial analysis
        analysis_v1 = self.generate_analysis(symbol, data)
        
        # Evaluate
        evaluation_v1 = self.evaluate_quality(analysis_v1)
        self.iteration_history.append({'version': 1, 'analysis': analysis_v1, 'evaluation': evaluation_v1})
        
        # Optimize
        analysis_v2 = self.optimize_analysis(analysis_v1, evaluation_v1)
        
        # Re-evaluate optimized version
        evaluation_v2 = self.evaluate_quality(analysis_v2)
        self.iteration_history.append({'version': 2, 'analysis': analysis_v2, 'evaluation': evaluation_v2})
        
        return {
            'workflow': 'evaluator_optimizer',
            'symbol': symbol,
            'final_analysis': analysis_v2,
            'final_evaluation': evaluation_v2,
            'improvement': evaluation_v2['quality_score'] - evaluation_v1['quality_score'],
            'iterations': len(self.iteration_history)
        }