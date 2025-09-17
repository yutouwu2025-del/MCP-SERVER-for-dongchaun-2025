#!/usr/bin/env python3
"""
Web Server for Rainfall MCP Server Status Monitoring

A simple web interface to monitor MCP server status and test rainfall data queries.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from mcp_server.tools import rainfall_tools
from ai_service.analyzer import get_analyzer


class RainfallWebHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for rainfall MCP server web interface"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(project_root), **kwargs)

    def end_headers(self):
        # 添加CORS头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        """处理GET请求"""
        if self.path == '/' or self.path == '/index.html':
            self.path = '/web_interface.html'

        super().do_GET()

    def do_POST(self):
        """处理POST请求 - API接口"""
        try:
            if self.path == '/api/status':
                self.handle_status_check()
            elif self.path == '/api/query':
                self.handle_query_rainfall()
            elif self.path == '/api/analyze':
                self.handle_analyze_rainfall()
            elif self.path == '/api/summary':
                self.handle_rainfall_summary()
            elif self.path == '/api/extreme':
                self.handle_extreme_events()
            elif self.path == '/api/test-deepseek':
                self.handle_test_deepseek()
            elif self.path == '/api/analyze-all':
                self.handle_analyze_all_data()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            logging.error(f"Error handling POST request: {e}")
            self.send_json_response({'error': str(e)}, 500)

    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(response.encode('utf-8'))

    def get_post_data(self):
        """获取POST数据"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                return json.loads(post_data.decode('utf-8'))
            return {}
        except Exception as e:
            logging.error(f"Error parsing POST data: {e}")
            return {}

    def handle_status_check(self):
        """处理状态检查 - 简化版本"""
        try:
            # 简单的状态检查，避免复杂的依赖

            # 1. 检查数据文件 - 支持多种格式
            data_dir = Path(project_root) / "data"
            data_files = []
            total_records = 0

            if data_dir.exists():
                # 检查多种数据文件格式
                csv_files = list(data_dir.glob("*.csv"))
                txt_files = list(data_dir.glob("*.txt"))
                xlsx_files = list(data_dir.glob("*.xlsx"))

                all_data_files = csv_files + txt_files + xlsx_files
                data_files = [f.stem for f in all_data_files]

                # 简单统计记录数（只检查前几个文件避免太慢）
                for data_file in all_data_files[:3]:
                    try:
                        if data_file.suffix.lower() in ['.csv', '.txt']:
                            with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = sum(1 for line in f) - 1  # 减去标题行
                                total_records += max(0, lines)
                        elif data_file.suffix.lower() == '.xlsx':
                            # 对于Excel文件，估算记录数
                            total_records += 300  # 估算值
                    except:
                        continue

            # 2. 检查API配置
            try:
                api_configured = bool(settings.deepseek_config.get('api_key'))
            except:
                api_configured = False

            # 3. 检查MCP工具状态
            mcp_tools_available = False
            try:
                from mcp_server.tools import rainfall_tools
                # 尝试获取工具定义来验证MCP功能
                tools = rainfall_tools.get_tool_definitions()
                mcp_tools_available = len(tools) > 0
            except:
                mcp_tools_available = False

            # 4. 组装状态信息
            status = {
                'server': {
                    'running': True,
                    'version': '1.0.0',
                    'port': 8081,
                    'name': 'rainfall-query-server'
                },
                'ai': {
                    'configured': api_configured,
                    'provider': 'DeepSeek',
                    'model': 'deepseek-chat',
                    'api_key_present': api_configured,
                    'base_url': 'https://api.deepseek.com'
                },
                'data': {
                    'files_found': len(data_files),
                    'files': data_files,
                    'total_records': total_records,
                    'file_types': list(set([f.suffix for f in all_data_files])) if all_data_files else []
                },
                'mcp': {
                    'tools_available': mcp_tools_available,
                    'tools_count': len(tools) if mcp_tools_available else 0,
                    'status': 'ready' if mcp_tools_available else 'unavailable'
                },
                'system': {
                    'platform': 'Windows',
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                    'mcp_version': '0.5.x'
                }
            }

            self.send_json_response(status)

        except Exception as e:
            # 如果出错，返回基本状态
            basic_status = {
                'server': {
                    'running': True,
                    'version': '1.0.0',
                    'port': 8081,
                    'name': 'rainfall-query-server'
                },
                'ai': {
                    'configured': False,
                    'provider': 'DeepSeek',
                    'model': 'deepseek-chat',
                    'api_key_present': False,
                    'base_url': 'https://api.deepseek.com'
                },
                'data': {
                    'files_found': 0,
                    'files': [],
                    'total_records': 0
                },
                'system': {
                    'platform': 'Windows',
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                    'mcp_version': '0.5.x',
                    'error': str(e)
                }
            }
            self.send_json_response(basic_status)

    def handle_query_rainfall(self):
        """处理降雨数据查询"""
        try:
            data = self.get_post_data()
            filename = data.get('filename', 'Dabaini')
            limit = data.get('limit', 10)
            filters = data.get('filters', {})

            # 直接调用查询函数，避免事件循环问题
            def run_async_query():
                try:
                    # Windows环境下使用新的事件循环
                    if sys.platform == "win32":
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        result = loop.run_until_complete(
                            rainfall_tools.query_rainfall(filename, filters, limit)
                        )
                        return result
                    finally:
                        loop.close()
                except Exception as e:
                    logging.error(f"Async query error: {e}")
                    raise

            result = run_async_query()
            if result and len(result) > 0 and hasattr(result[0], 'text'):
                try:
                    response_data = json.loads(result[0].text)
                    self.send_json_response(response_data)
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error: {e}, text: {result[0].text[:500]}")
                    self.send_json_response({'error': '数据解析失败', 'raw_text': result[0].text[:500]}, 500)
            else:
                logging.error(f"Invalid result format: {result}")
                self.send_json_response({'error': '查询返回格式错误'}, 500)

        except Exception as e:
            logging.error(f"Error in query rainfall: {e}")
            self.send_json_response({'error': str(e), 'details': f'查询失败: {str(e)}'}, 500)

    def handle_analyze_rainfall(self):
        """处理AI分析请求"""
        try:
            data = self.get_post_data()
            filename = data.get('filename', 'Dabaini')
            question = data.get('question', '')

            if not question:
                self.send_json_response({'error': 'Question is required', 'message': '请输入分析问题'}, 400)
                return

            def run_async_analysis():
                try:
                    if sys.platform == "win32":
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        result = loop.run_until_complete(
                            rainfall_tools.analyze_rainfall(filename, question)
                        )
                        return result
                    finally:
                        loop.close()
                except Exception as e:
                    logging.error(f"Async analysis error: {e}")
                    raise

            result = run_async_analysis()
            if result and len(result) > 0 and hasattr(result[0], 'text'):
                try:
                    response_data = json.loads(result[0].text)
                    self.send_json_response(response_data)
                except json.JSONDecodeError as e:
                    logging.error(f"JSON decode error in analysis: {e}")
                    self.send_json_response({'error': '分析结果解析失败', 'raw_text': result[0].text[:500]}, 500)
            else:
                self.send_json_response({'error': 'AI分析返回格式错误'}, 500)

        except Exception as e:
            logging.error(f"Error in analyze rainfall: {e}")
            self.send_json_response({'error': str(e), 'details': f'AI分析失败: {str(e)}'}, 500)

    def handle_rainfall_summary(self):
        """处理统计摘要请求"""
        try:
            data = self.get_post_data()
            filename = data.get('filename', 'Dabaini')
            include_ai = data.get('include_ai_analysis', False)

            def run_async_summary():
                try:
                    if sys.platform == "win32":
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        result = loop.run_until_complete(
                            rainfall_tools.rainfall_summary(filename, include_ai)
                        )
                        return result
                    finally:
                        loop.close()
                except Exception as e:
                    logging.error(f"Async summary error: {e}")
                    raise

            result = run_async_summary()
            response_data = json.loads(result[0].text)
            self.send_json_response(response_data)

        except Exception as e:
            logging.error(f"Error in rainfall summary: {e}")
            self.send_json_response({'error': str(e), 'details': f'摘要生成失败: {str(e)}'}, 500)

    def handle_extreme_events(self):
        """处理极端事件检测"""
        try:
            data = self.get_post_data()
            filename = data.get('filename', 'Dabaini')
            threshold = data.get('threshold_percentile', 95)
            limit = data.get('limit', 10)

            def run_async_extreme():
                try:
                    if sys.platform == "win32":
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        result = loop.run_until_complete(
                            rainfall_tools.extreme_events(filename, threshold, limit)
                        )
                        return result
                    finally:
                        loop.close()
                except Exception as e:
                    logging.error(f"Async extreme events error: {e}")
                    raise

            result = run_async_extreme()
            response_data = json.loads(result[0].text)
            self.send_json_response(response_data)

        except Exception as e:
            logging.error(f"Error in extreme events: {e}")
            self.send_json_response({'error': str(e), 'details': f'极端事件检测失败: {str(e)}'}, 500)

    def handle_test_deepseek(self):
        """处理DeepSeek API测试"""
        try:
            def run_async_test():
                try:
                    if sys.platform == "win32":
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    async def test_api():
                        analyzer = None
                        try:
                            analyzer = get_analyzer()

                            # 测试数据
                            test_data = {
                                "filename": "test",
                                "basic_statistics": {
                                    "count": 100,
                                    "mean": 5.5,
                                    "max": 25.0
                                }
                            }

                            # 发送测试请求
                            result = await analyzer.analyze_data(test_data, "这是一个API连接测试，请简短回复确认连接正常")

                            return result

                        except Exception as e:
                            logging.error(f"DeepSeek test error: {e}")
                            return {"success": False, "error": str(e)}
                        finally:
                            if analyzer:
                                try:
                                    await analyzer.close()
                                except:
                                    pass

                    try:
                        test_result = loop.run_until_complete(test_api())
                        return test_result
                    finally:
                        loop.close()

                except Exception as e:
                    logging.error(f"Async test error: {e}")
                    return {"success": False, "error": str(e)}

            test_result = run_async_test()

            if test_result.get('success'):
                response = {
                    'status': 'success',
                    'message': 'DeepSeek API 连接正常',
                    'model': 'deepseek-chat',
                    'test_response': str(test_result.get('analysis', '测试成功'))[:200] + '...'
                }
            else:
                response = {
                    'status': 'error',
                    'message': 'DeepSeek API 连接失败',
                    'error': test_result.get('error', 'Unknown error')
                }

            self.send_json_response(response)

        except Exception as e:
            logging.error(f"Error testing DeepSeek: {e}")
            self.send_json_response({
                'status': 'error',
                'message': 'API测试失败',
                'error': str(e),
                'details': f'DeepSeek测试失败: {str(e)}'
            }, 500)

    def handle_analyze_all_data(self):
        """处理全数据综合分析请求"""
        try:
            data = self.get_post_data()
            analysis_type = data.get('analysis_type', 'general')
            question = data.get('question', None)

            def run_async_analyze_all():
                try:
                    if sys.platform == "win32":
                        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)

                    try:
                        result = loop.run_until_complete(
                            rainfall_tools.analyze_all_rainfall_data(question, analysis_type)
                        )
                        return result
                    finally:
                        loop.close()
                except Exception as e:
                    logging.error(f"Async analyze all data error: {e}")
                    raise

            result = run_async_analyze_all()
            response_data = json.loads(result[0].text)
            self.send_json_response(response_data)

        except Exception as e:
            logging.error(f"Error in analyze all data: {e}")
            self.send_json_response({'error': str(e), 'details': f'全数据分析失败: {str(e)}'}, 500)

    def log_message(self, format, *args):
        """自定义日志消息格式"""
        logging.info(f"{self.address_string()} - {format % args}")


def start_web_server(port=8081):
    """启动Web服务器"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    try:
        server_address = ('', port)
        httpd = HTTPServer(server_address, RainfallWebHandler)

        logger.info(f"🌐 Web服务器启动成功!")
        logger.info(f"📍 访问地址: http://localhost:{port}")
        logger.info(f"📍 局域网访问: http://[您的IP地址]:{port}")
        logger.info(f"📁 服务目录: {project_root}")
        logger.info("按 Ctrl+C 停止服务器")

        httpd.serve_forever()

    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")


if __name__ == "__main__":
    # Windows环境优化
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    start_web_server()