"""
AI Models configuration for modular AI service support
"""
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CLAUDE = "claude"


class ModelConfig(BaseModel):
    """AI Model configuration"""
    provider: ModelProvider
    model_name: str
    base_url: str
    api_key: str
    timeout: int = 60
    max_retries: int = 3
    temperature: float = 0.7
    max_tokens: int = 2000


class ModelsManager:
    """Manage multiple AI model configurations"""

    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self._setup_default_models()

    def _setup_default_models(self):
        """Setup default model configurations"""
        from .settings import settings

        deepseek_config = settings.deepseek_config
        self.models["deepseek-chat"] = ModelConfig(
            provider=ModelProvider.DEEPSEEK,
            model_name="deepseek-chat",
            base_url=deepseek_config.get('base_url', 'https://api.deepseek.com'),
            api_key=deepseek_config.get('api_key', ''),
            timeout=deepseek_config.get('timeout', 60),
            max_retries=deepseek_config.get('max_retries', 3),
            temperature=0.3,
            max_tokens=2000
        )

    def get_model(self, model_name: str = "deepseek-chat") -> Optional[ModelConfig]:
        """Get model configuration by name"""
        return self.models.get(model_name)

    def add_model(self, name: str, config: ModelConfig):
        """Add a new model configuration"""
        self.models[name] = config

    def list_models(self) -> list:
        """List all available models"""
        return list(self.models.keys())

    def get_default_model(self) -> ModelConfig:
        """Get default model configuration"""
        return self.models.get("deepseek-chat", list(self.models.values())[0])


# Global models manager instance
models_manager = ModelsManager()