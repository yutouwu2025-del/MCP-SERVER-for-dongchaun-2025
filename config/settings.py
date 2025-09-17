"""
Configuration settings for rainfall MCP server
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Settings:
    def __init__(self, config_file: Optional[str] = None):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.config_file = config_file or self.base_dir / "deepseekkey.txt"

        self.ai_config = self._load_ai_config()
        self.server_config = self._get_server_config()

    def _load_ai_config(self) -> Dict[str, Any]:
        """Load AI model configuration from deepseekkey.txt"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            config = {}
            lines = content.strip().split('\n')

            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue

                if ':' in line:
                    # 移除注释部分
                    if '#' in line:
                        line = line.split('#')[0].strip()

                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if key == "base_url":
                        config['base_url'] = value
                    elif key == "api_token":
                        config['api_key'] = value
                    elif key == "timeout":
                        config['timeout'] = int(value)
                    elif key == "max_retries":
                        config['max_retries'] = int(value)

            # 验证必要的配置项
            if not config.get('base_url'):
                config['base_url'] = 'https://api.deepseek.com'
            if not config.get('api_key'):
                print("Warning: API key not found in configuration")

            return config
        except Exception as e:
            print(f"Error loading AI config: {e}")
            return {
                'base_url': 'https://api.deepseek.com',
                'api_key': '',
                'timeout': 60,
                'max_retries': 3
            }

    def _get_server_config(self) -> Dict[str, Any]:
        """Get MCP server configuration"""
        return {
            'name': 'rainfall-query-server',
            'version': '1.0.0',
            'description': 'MCP Server for rainfall data query and analysis',
            'host': '0.0.0.0',  # 局域网访问
            'port': 8080,
            'debug': False
        }

    @property
    def deepseek_config(self) -> Dict[str, Any]:
        """Get DeepSeek API configuration"""
        return self.ai_config

    def get_data_files(self) -> list:
        """Get list of available data files"""
        data_files = []
        for file_path in self.data_dir.glob("*.xlsx"):
            if not file_path.name.startswith('~'):  # 跳过临时文件
                data_files.append(file_path)
        return data_files


# Global settings instance
settings = Settings()