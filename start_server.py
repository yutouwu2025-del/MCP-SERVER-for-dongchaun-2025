#!/usr/bin/env python3
"""
Simple startup script for Rainfall MCP Server
Handles MCP 0.5.x compatibility and proper tool registration
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from config.settings import settings
from mcp_server.tools import rainfall_tools


async def main():
    """启动MCP服务器"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("rainfall_mcp")

    # 创建服务器
    server = Server("rainfall-query-server")

    # 获取所有工具定义
    tools_definitions = rainfall_tools.get_tool_definitions()

    # 注册list_tools处理器
    @server.list_tools()
    async def list_tools():
        return tools_definitions

    # 注册call_tool处理器
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """处理工具调用"""
        try:
            logger.info(f"调用工具: {name}, 参数: {arguments}")

            if name == "query_rainfall":
                return await rainfall_tools.query_rainfall(**arguments)
            elif name == "analyze_rainfall":
                return await rainfall_tools.analyze_rainfall(**arguments)
            elif name == "rainfall_summary":
                return await rainfall_tools.rainfall_summary(**arguments)
            elif name == "list_datasets":
                return await rainfall_tools.list_datasets(**arguments)
            elif name == "extreme_events":
                return await rainfall_tools.extreme_events(**arguments)
            elif name == "compare_periods":
                return await rainfall_tools.compare_periods(**arguments)
            else:
                return [TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

        except Exception as e:
            logger.error(f"工具执行错误 {name}: {e}")
            return [TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}"
            )]

    # 启动服务器
    logger.info("启动降雨量查询MCP服务器...")
    logger.info(f"数据目录: {settings.data_dir}")

    # 检查数据文件
    data_files = settings.get_data_files()
    if data_files:
        logger.info(f"找到 {len(data_files)} 个数据文件:")
        for file_path in data_files:
            logger.info(f"  - {file_path.name}")
    else:
        logger.warning("数据目录中未找到数据文件")

    # 检查AI配置
    if settings.deepseek_config.get('api_key'):
        logger.info("DeepSeek API 配置成功")
    else:
        logger.warning("未找到 DeepSeek API 密钥")

    logger.info(f"注册了 {len(tools_definitions)} 个MCP工具")

    # 运行服务器
    async with stdio_server() as streams:
        await server.run(
            streams[0],  # stdin
            streams[1],  # stdout
            server.create_initialization_options()
        )


if __name__ == "__main__":
    # Windows环境优化
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)