"""
DeepSeek API client for rainfall data analysis
"""
import httpx
import json
import asyncio
from typing import Dict, Any, Optional, List
import logging
from config.models import ModelConfig, ModelProvider


class DeepSeekClient:
    """DeepSeek API client"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        if config.provider != ModelProvider.DEEPSEEK:
            raise ValueError("This client only supports DeepSeek models")

        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
        )

    async def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        """Send chat completion request to DeepSeek API"""
        try:
            payload = {
                "model": self.config.model_name,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "stream": False
            }

            self.logger.debug(f"Sending request to DeepSeek API: {payload}")

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            self.logger.info("Successfully received response from DeepSeek API")
            return content

        except httpx.RequestError as e:
            self.logger.error(f"Request error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            return None
        except KeyError as e:
            self.logger.error(f"Unexpected response format: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return None

    async def analyze_rainfall_data(self, data_summary: Dict[str, Any], question: str = None) -> Optional[str]:
        """Analyze rainfall data using AI"""
        try:
            # 构建系统提示
            system_prompt = """你是一个专业的气象数据分析专家。你的任务是分析降雨量数据，提供准确、有用的分析结果。

请根据提供的数据进行分析，包括但不限于：
1. 数据概况总结
2. 降雨模式分析
3. 异常事件识别
4. 趋势分析
5. 实用建议

请用中文回答，保持专业性和准确性。如果数据不足以支持某些分析，请明确说明。"""

            # 构建用户消息
            data_str = json.dumps(data_summary, ensure_ascii=False, indent=2)

            if question:
                user_message = f"""请分析以下降雨量数据并回答问题：

问题：{question}

数据摘要：
{data_str}

请提供详细分析。"""
            else:
                user_message = f"""请分析以下降雨量数据：

{data_str}

请提供全面的分析报告，包括数据概况、模式分析、异常事件和趋势等。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            return await self.chat_completion(messages)

        except Exception as e:
            self.logger.error(f"Error analyzing rainfall data: {e}")
            return None

    async def answer_question(self, data_summary: Dict[str, Any], question: str) -> Optional[str]:
        """Answer specific questions about rainfall data"""
        return await self.analyze_rainfall_data(data_summary, question)

    async def generate_summary(self, data_summary: Dict[str, Any]) -> Optional[str]:
        """Generate a summary report of rainfall data"""
        try:
            system_prompt = """你是一个专业的气象数据分析师。请为降雨量数据生成一份简洁但全面的摘要报告。

报告应包括：
1. 数据基本信息（时间范围、地区、记录数量）
2. 主要统计指标
3. 重要发现和模式
4. 异常事件（如有）
5. 简要结论

请使用专业但易懂的语言，用中文回答。"""

            data_str = json.dumps(data_summary, ensure_ascii=False, indent=2)

            user_message = f"""请为以下降雨量数据生成摘要报告：

{data_str}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            return await self.chat_completion(messages)

        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()