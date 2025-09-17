"""
AI-powered rainfall data analyzer
"""
import logging
from typing import Dict, Any, Optional, List
from config.models import models_manager, ModelProvider
from .deepseek import DeepSeekClient


class RainfallAnalyzer:
    """AI-powered rainfall data analyzer with modular model support"""

    def __init__(self, model_name: str = "deepseek-chat"):
        self.model_name = model_name
        self.model_config = models_manager.get_model(model_name)
        self.logger = logging.getLogger(__name__)

        if not self.model_config:
            raise ValueError(f"Model '{model_name}' not found in configuration")

        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate AI client based on model provider"""
        if self.model_config.provider == ModelProvider.DEEPSEEK:
            self.client = DeepSeekClient(self.model_config)
        else:
            raise NotImplementedError(f"Provider {self.model_config.provider} not implemented yet")

    async def analyze_data(self, data_summary: Dict[str, Any], question: str = None) -> Dict[str, Any]:
        """Analyze rainfall data with AI assistance"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "AI client not initialized"
                }

            # 获取AI分析结果
            if question:
                analysis = await self.client.answer_question(data_summary, question)
            else:
                analysis = await self.client.analyze_rainfall_data(data_summary)

            if analysis:
                return {
                    "success": True,
                    "analysis": analysis,
                    "model_used": self.model_name,
                    "data_summary": data_summary
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to get AI analysis"
                }

        except Exception as e:
            self.logger.error(f"Error in analyze_data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def generate_summary_report(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive summary report"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "AI client not initialized"
                }

            summary = await self.client.generate_summary(data_summary)

            if summary:
                return {
                    "success": True,
                    "summary": summary,
                    "model_used": self.model_name,
                    "report_type": "ai_summary"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate summary report"
                }

        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def answer_question(self, data_summary: Dict[str, Any], question: str) -> Dict[str, Any]:
        """Answer specific questions about rainfall data"""
        if not question.strip():
            return {
                "success": False,
                "error": "Question cannot be empty"
            }

        return await self.analyze_data(data_summary, question)

    async def compare_periods(self, data1: Dict[str, Any], data2: Dict[str, Any],
                            period1_name: str = "Period 1", period2_name: str = "Period 2") -> Dict[str, Any]:
        """Compare rainfall data between two periods"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "AI client not initialized"
                }

            comparison_prompt = f"""请比较以下两个时期的降雨量数据：

{period1_name}数据：
{data1}

{period2_name}数据：
{data2}

请提供详细的比较分析，包括：
1. 降雨量变化
2. 模式差异
3. 异常事件对比
4. 可能的原因分析
5. 趋势预测"""

            analysis = await self.client.chat_completion([
                {"role": "system", "content": "你是专业的气象数据分析师，请提供准确的数据比较分析。"},
                {"role": "user", "content": comparison_prompt}
            ])

            if analysis:
                return {
                    "success": True,
                    "comparison": analysis,
                    "period1_name": period1_name,
                    "period2_name": period2_name,
                    "model_used": self.model_name
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate comparison analysis"
                }

        except Exception as e:
            self.logger.error(f"Error comparing periods: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def predict_trends(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Predict rainfall trends based on historical data"""
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "AI client not initialized"
                }

            trend_prompt = f"""基于以下降雨量历史数据，请分析趋势并做出预测：

{data_summary}

请提供：
1. 历史趋势分析
2. 模式识别
3. 短期预测（未来几个月）
4. 长期趋势预测
5. 不确定性和风险评估
6. 建议和预防措施

请保持客观和科学的态度，明确指出预测的局限性。"""

            prediction = await self.client.chat_completion([
                {"role": "system", "content": "你是专业的气象预测分析师，请基于数据提供科学的趋势分析和预测。"},
                {"role": "user", "content": trend_prompt}
            ])

            if prediction:
                return {
                    "success": True,
                    "prediction": prediction,
                    "model_used": self.model_name,
                    "analysis_type": "trend_prediction"
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate trend prediction"
                }

        except Exception as e:
            self.logger.error(f"Error predicting trends: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """Close AI client connections"""
        if self.client:
            await self.client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


def get_analyzer(model_name: str = None) -> RainfallAnalyzer:
    """Factory function to get analyzer instance"""
    if model_name is None:
        model_name = "deepseek-chat"

    return RainfallAnalyzer(model_name)