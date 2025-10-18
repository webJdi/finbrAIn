# src/utils/config.py
import os
from dotenv import load_dotenv
from smolagents import CodeAgent, LiteLLMModel

load_dotenv()

class FinancialAgentConfig:
    def __init__(self):
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.model_name = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        self.base_url = os.getenv('OPENROUTER_BASE_URL')
        
    def get_model(self):
        return LiteLLMModel(
            model_id=self.model_name,
            api_key=self.openrouter_api_key,
            base_url=self.base_url
        )