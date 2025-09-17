#!/usr/bin/env python3
"""
Rainfall Data Query MCP Server

A Model Context Protocol (MCP) server for querying and analyzing rainfall data
with AI-powered insights using DeepSeek and other models.

Usage:
    python main.py [--host HOST] [--port PORT] [--debug]

Features:
- Query rainfall data with filters
- AI-powered data analysis using DeepSeek
- Statistical summaries and reports
- Extreme weather event detection
- Period comparison analysis
- Modular AI model support
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent
except ImportError:
    print("Error: MCP package not found. Please install with: pip install mcp==0.5.2")
    sys.exit(1)

from config.settings import settings
from mcp_server.tools import rainfall_tools


class RainfallMCPServer:
    """Rainfall Data Query MCP Server"""

    def __init__(self):
        self.server = Server(settings.server_config['name'])
        self.tools = rainfall_tools
        self.logger = self._setup_logging()

        # 注册所有工具
        self._register_tools()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('rainfall_mcp_server.log')
            ]
        )
        return logging.getLogger(__name__)

    def _register_tools(self):
        """Register all MCP tools"""
        tools_list = self.tools.get_tools()

        for tool in tools_list:
            self.server.list_tools = lambda: tools_list

            # 注册工具处理函数
            if tool.name == "query_rainfall":
                self.server.call_tool = self._create_tool_handler(self.tools.query_rainfall)
            elif tool.name == "analyze_rainfall":
                self.server.call_tool = self._create_tool_handler(self.tools.analyze_rainfall)
            elif tool.name == "rainfall_summary":
                self.server.call_tool = self._create_tool_handler(self.tools.rainfall_summary)
            elif tool.name == "list_datasets":
                self.server.call_tool = self._create_tool_handler(self.tools.list_datasets)
            elif tool.name == "extreme_events":
                self.server.call_tool = self._create_tool_handler(self.tools.extreme_events)
            elif tool.name == "compare_periods":
                self.server.call_tool = self._create_tool_handler(self.tools.compare_periods)

        self.logger.info(f"Registered {len(tools_list)} MCP tools")

    def _create_tool_handler(self, tool_func):
        """Create a tool handler that wraps the tool function"""
        async def handler(name: str, arguments: dict):
            if name == tool_func.__name__:
                try:
                    self.logger.info(f"Executing tool: {name} with arguments: {arguments}")
                    result = await tool_func(**arguments)
                    return result
                except Exception as e:
                    self.logger.error(f"Error executing tool {name}: {e}")
                    return [TextContent(
                        type="text",
                        text=f"Error executing tool {name}: {str(e)}"
                    )]
            return []

        return handler

    async def run_stdio(self):
        """Run server with stdio transport"""
        self.logger.info("Starting Rainfall MCP Server with stdio transport")
        self.logger.info(f"Server: {settings.server_config['name']} v{settings.server_config['version']}")
        self.logger.info(f"Data directory: {settings.data_dir}")

        # 检查数据文件
        data_files = settings.get_data_files()
        if data_files:
            self.logger.info(f"Found {len(data_files)} data files:")
            for file_path in data_files:
                self.logger.info(f"  - {file_path.name}")
        else:
            self.logger.warning("No data files found in data directory")

        # 检查AI配置
        if settings.deepseek_config.get('api_key'):
            self.logger.info("DeepSeek API configured successfully")
        else:
            self.logger.warning("DeepSeek API key not found")

        try:
            async with stdio_server() as streams:
                await self.server.run(
                    streams[0],  # stdin
                    streams[1],  # stdout
                    self.server.create_initialization_options()
                )
        except KeyboardInterrupt:
            self.logger.info("Server stopped by user")
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise

    async def run_network(self, host: str = "0.0.0.0", port: int = 8080):
        """Run server with network transport (for LAN access)"""
        self.logger.info(f"Starting Rainfall MCP Server on {host}:{port}")
        self.logger.warning("Network transport not implemented in MCP 0.5.x")
        self.logger.info("Use stdio transport instead")
        await self.run_stdio()


def create_argparser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Rainfall Data Query MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                    # Run with stdio transport
    python main.py --debug            # Run with debug logging
    python main.py --host 0.0.0.0     # Network mode (fallback to stdio)

MCP Tools Available:
    - query_rainfall: Query rainfall data with filters
    - analyze_rainfall: AI-powered data analysis
    - rainfall_summary: Statistical summaries
    - list_datasets: List available datasets
    - extreme_events: Detect extreme weather events
    - compare_periods: Compare different time periods
        """
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind to (default: 8080)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "network"],
        default="stdio",
        help="Transport type (default: stdio)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Rainfall MCP Server v{settings.server_config['version']}"
    )

    return parser


async def main():
    """Main entry point"""
    parser = create_argparser()
    args = parser.parse_args()

    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # 创建并运行服务器
    server = RainfallMCPServer()

    try:
        if args.transport == "network":
            await server.run_network(args.host, args.port)
        else:
            await server.run_stdio()
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Windows 环境下使用 ProactorEventLoop
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())