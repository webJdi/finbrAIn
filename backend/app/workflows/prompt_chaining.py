from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
import json
import re
from datetime import datetime
import asyncio
import os

class NewsProcessingChain:
    """
    Implements the Prompt Chaining workflow:
    Ingest News → Preprocess → Classify → Extract → Summarize
    """
    
    def __init__(self, llm_model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            model=llm_model,
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.output_parser = StrOutputParser()
    
    def _create_ingestion_chain(self):
        """Step 1: Ingest and validate news data"""
        
        ingest_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a news data validator. Your job is to:
            1. Validate that the input contains valid news articles
            2. Check for required fields (title, content, date, source)
            3. Filter out invalid or incomplete articles
            4. Return a standardized JSON structure
            
            Return only valid articles in this format:
            {
                "valid_articles": [
                    {
                        "title": "article title",
                        "content": "article content",
                        "date": "publication date",
                        "source": "news source",
                        "url": "article url if available"
                    }
                ],
                "rejected_count": number_of_rejected_articles,
                "rejection_reasons": ["reason1", "reason2"]
            }"""),
            ("human", "Validate and standardize this news data: {raw_news}")
        ])
        
        return ingest_prompt | self.llm | self.output_parser
    
    def _create_preprocessing_chain(self):
        """Step 2: Preprocess the news text"""
        
        preprocess_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a text preprocessor for financial news. Clean and prepare the text by:
            1. Removing HTML tags and special characters
            2. Normalizing text encoding
            3. Extracting key entities (companies, people, dates, numbers)
            4. Removing duplicate sentences or redundant information
            5. Standardizing financial terms and symbols
            
            Return preprocessed articles with extracted entities:
            {
                "preprocessed_articles": [
                    {
                        "title": "cleaned title",
                        "content": "cleaned and normalized content",
                        "entities": {
                            "companies": ["AAPL", "Apple Inc"],
                            "people": ["Tim Cook"],
                            "dates": ["2024-01-15"],
                            "financial_terms": ["earnings", "revenue"],
                            "numbers": ["$50B", "15%"]
                        },
                        "metadata": {
                            "word_count": 150,
                            "readability_score": "medium"
                        }
                    }
                ]
            }"""),
            ("human", "Preprocess these validated articles: {validated_news}")
        ])
        
        return preprocess_prompt | self.llm | self.output_parser
    
    def _create_classification_chain(self):
        """Step 3: Classify news articles by type and sentiment"""
        
        classify_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial news classifier. Classify each article by:
            
            1. News Type:
               - earnings_report
               - merger_acquisition
               - product_launch
               - regulatory_news
               - market_analysis
               - executive_change
               - analyst_rating
               - general_corporate
            
            2. Sentiment: positive, negative, neutral
            
            3. Impact Level: high, medium, low
            
            4. Time Sensitivity: breaking, recent, historical
            
            5. Market Relevance: stock_specific, sector_wide, market_wide
            
            Return classification results:
            {
                "classified_articles": [
                    {
                        "title": "article title",
                        "classifications": {
                            "news_type": "earnings_report",
                            "sentiment": "positive",
                            "impact_level": "high",
                            "time_sensitivity": "breaking",
                            "market_relevance": "stock_specific"
                        },
                        "confidence_scores": {
                            "news_type": 0.95,
                            "sentiment": 0.87
                        }
                    }
                ]
            }"""),
            ("human", "Classify these preprocessed articles: {preprocessed_news}")
        ])
        
        return classify_prompt | self.llm | self.output_parser
    
    def _create_extraction_chain(self):
        """Step 4: Extract key information and insights"""
        
        extract_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial information extractor. From each classified article, extract:
            
            1. Key Facts:
               - Financial figures (revenue, profit, losses)
               - Dates and timelines
               - Company actions or decisions
               - Market performance data
            
            2. Investment Implications:
               - Potential stock price impact
               - Sector implications
               - Risk factors mentioned
               - Growth opportunities
            
            3. Stakeholder Impact:
               - Effect on shareholders
               - Impact on customers
               - Regulatory implications
               - Competitive positioning
            
            Return extracted information:
            {
                "extracted_articles": [
                    {
                        "title": "article title",
                        "key_facts": {
                            "financial_figures": ["Q3 revenue $50B", "EPS $1.25"],
                            "important_dates": ["2024-01-15", "Q4 2024"],
                            "company_actions": ["stock buyback program"],
                            "market_data": ["stock up 5%"]
                        },
                        "investment_implications": {
                            "price_impact": "positive",
                            "sector_effect": "technology sector boost",
                            "risk_factors": ["supply chain concerns"],
                            "opportunities": ["AI market expansion"]
                        },
                        "stakeholder_impact": {
                            "shareholders": "positive earnings surprise",
                            "customers": "new product launch",
                            "regulatory": "increased scrutiny",
                            "competitive": "market share gain"
                        }
                    }
                ]
            }"""),
            ("human", "Extract key information from these classified articles: {classified_news}")
        ])
        
        return extract_prompt | self.llm | self.output_parser
    
    def _create_summarization_chain(self):
        """Step 5: Summarize extracted information into actionable insights"""
        
        summarize_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial news summarizer. Create a comprehensive summary that includes:
            
            1. Executive Summary:
               - Most important developments
               - Overall market sentiment
               - Key takeaways for investors
            
            2. Investment Analysis:
               - Bullish factors
               - Bearish factors
               - Neutral factors
               - Overall investment outlook
            
            3. Risk Assessment:
               - Immediate risks
               - Long-term concerns
               - Mitigation strategies
            
            4. Action Items:
               - Recommended actions for investors
               - Monitoring points
               - Timeline considerations
            
            5. Market Context:
               - Broader market implications
               - Sector-wide effects
               - Economic indicators relevance
            
            Make the summary concise but comprehensive, actionable, and investor-focused."""),
            ("human", """Summarize these extracted articles into actionable investment insights:
            
            Extracted Information: {extracted_news}
            
            Context: This analysis is for investment decision-making purposes.""")
        ])
        
        return summarize_prompt | self.llm | self.output_parser
    
    def _parse_json_output(self, output: str) -> Dict[str, Any]:
        """Parse JSON output from LLM, with fallback handling"""
        try:
            # Try to find JSON in the output
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Return structured fallback
                return {"error": "No valid JSON found", "raw_output": output}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw_output": output}
    
    async def process_news(self, raw_news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main method to process news through the complete chain:
        Ingest → Preprocess → Classify → Extract → Summarize
        """
        
        try:
            # Step 1: Ingest and validate
            print("🔄 Step 1: Ingesting and validating news data...")
            ingest_chain = self._create_ingestion_chain()
            ingested_result = await ingest_chain.ainvoke({"raw_news": json.dumps(raw_news_data)})
            ingested_data = self._parse_json_output(ingested_result)
            
            if "error" in ingested_data:
                print(f"❌ Ingestion failed: {ingested_data['error']}")
                return {"error": "Ingestion failed", "details": ingested_data}
            
            # Step 2: Preprocess
            print("🔄 Step 2: Preprocessing news content...")
            preprocess_chain = self._create_preprocessing_chain()
            preprocessed_result = await preprocess_chain.ainvoke({"validated_news": json.dumps(ingested_data)})
            preprocessed_data = self._parse_json_output(preprocessed_result)
            
            if "error" in preprocessed_data:
                print(f"❌ Preprocessing failed: {preprocessed_data['error']}")
                return {"error": "Preprocessing failed", "details": preprocessed_data}
            
            # Step 3: Classify
            print("🔄 Step 3: Classifying news articles...")
            classify_chain = self._create_classification_chain()
            classified_result = await classify_chain.ainvoke({"preprocessed_news": json.dumps(preprocessed_data)})
            classified_data = self._parse_json_output(classified_result)
            
            if "error" in classified_data:
                print(f"❌ Classification failed: {classified_data['error']}")
                return {"error": "Classification failed", "details": classified_data}
            
            # Step 4: Extract
            print("🔄 Step 4: Extracting key information...")
            extract_chain = self._create_extraction_chain()
            extracted_result = await extract_chain.ainvoke({"classified_news": json.dumps(classified_data)})
            extracted_data = self._parse_json_output(extracted_result)
            
            if "error" in extracted_data:
                print(f"❌ Extraction failed: {extracted_data['error']}")
                return {"error": "Extraction failed", "details": extracted_data}
            
            # Step 5: Summarize
            print("🔄 Step 5: Generating summary and insights...")
            summarize_chain = self._create_summarization_chain()
            summary_result = await summarize_chain.ainvoke({"extracted_news": json.dumps(extracted_data)})
            
            print("✅ News processing chain completed successfully!")
            
            return {
                "success": True,
                "processed_at": datetime.now().isoformat(),
                "chain_results": {
                    "ingested": ingested_data,
                    "preprocessed": preprocessed_data,
                    "classified": classified_data,
                    "extracted": extracted_data,
                    "summary": summary_result
                },
                "final_summary": summary_result,
                "metadata": {
                    "total_articles_processed": len(raw_news_data),
                    "valid_articles": len(ingested_data.get("valid_articles", [])),
                    "processing_time": "completed"
                }
            }
            
        except Exception as e:
            print(f"❌ News processing chain failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

# Example usage
async def main():
    # Sample news data
    sample_news = [
        {
            "title": "Apple Reports Record Q3 Earnings",
            "content": "Apple Inc. reported record third-quarter earnings with revenue of $50 billion...",
            "date": "2024-01-15",
            "source": "Financial Times",
            "url": "https://example.com/news1"
        },
        {
            "title": "Federal Reserve Signals Rate Cut",
            "content": "The Federal Reserve indicated potential interest rate cuts in the coming months...",
            "date": "2024-01-14",
            "source": "Reuters",
            "url": "https://example.com/news2"
        }
    ]
    
    processor = NewsProcessingChain()
    result = await processor.process_news(sample_news)
    
    if result.get("success"):
        print("Final Summary:", result["final_summary"])
    else:
        print("Processing failed:", result.get("error"))

if __name__ == "__main__":
    asyncio.run(main())