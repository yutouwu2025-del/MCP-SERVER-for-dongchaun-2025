# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 Model Context Protocol (MCP) 的降雨量数据查询和分析服务平台，集成 DeepSeek AI 模型进行智能数据分析。项目为中国科学院东川泥石流观测研究站提供降雨量数据服务。

## 开发命令

### 环境设置
```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥 (推荐使用助手)
python configure_api.py

# 或手动编辑 deepseekkey.txt
```

### 启动服务
```bash
# 一键启动所有服务 (推荐)
start_all.bat

# 单独启动 MCP 服务器
python start_server.py

# 单独启动 Web 服务器
python web_server.py

# 直接运行主程序
python main.py [--debug] [--host HOST] [--port PORT]
```

### 测试和调试
```bash
# 启用调试模式
python main.py --debug

# 检查服务状态
# 访问 http://localhost:8081 查看 Web 界面状态
```

## 核心架构

### 模块化设计
- **config/**: 配置管理模块
  - `settings.py`: 主配置文件，加载 deepseekkey.txt 中的 API 配置
  - `models.py`: AI 模型配置
- **data_handler/**: 数据处理模块
  - `reader.py`: 多格式数据读取器 (CSV/TXT/XLSX)
  - `processor.py`: 数据分析处理器
- **ai_service/**: AI 服务模块
  - `deepseek.py`: DeepSeek API 客户端
  - `analyzer.py`: 智能分析器
- **mcp_server/**: MCP 服务器模块
  - `tools.py`: 实现 7 个 MCP 工具的核心逻辑

### MCP 协议架构
- 使用 MCP 0.5.2 版本
- JSON-RPC 2.0 over stdio 通信协议
- 支持 7 个核心工具：
  - `query_rainfall`: 数据查询
  - `analyze_rainfall`: AI 智能分析
  - `rainfall_summary`: 统计摘要
  - `list_datasets`: 数据集列表
  - `extreme_events`: 极端事件检测
  - `compare_periods`: 时期比较分析
  - `analyze_all_rainfall_data`: 全数据综合分析

### 双服务架构
1. **MCP Server** (stdio): 为 AI 客户端提供工具接口
2. **Web Server** (HTTP:8081): 提供 Web 监控界面和状态检查

### 数据处理特性
- 支持多编码格式：UTF-8, GBK, GB2312
- 智能中文日期解析："2024年1月1日" 格式
- 多格式文件支持：XLSX, CSV, TXT
- 数据文件存储在 `data/` 目录

### AI 集成
- DeepSeek API 集成用于智能数据分析
- API 配置存储在 `deepseekkey.txt`
- 支持异步 AI 分析请求
- 包含错误处理和重试机制

## 重要文件路径

- **启动脚本**: `start_all.bat` - 一键启动脚本
- **主程序**: `main.py` - 程序入口点
- **配置文件**: `deepseekkey.txt` - API 密钥配置
- **数据目录**: `data/` - 降雨量数据文件存储位置
- **Web界面**: `web_interface.html` - 监控界面
- **依赖清单**: `requirements.txt` - Python 包依赖

## 开发注意事项

### Python 环境
- 需要 Python 3.8+
- Windows 环境使用 `WindowsProactorEventLoopPolicy`
- 支持异步编程模式

### 日志系统
- 日志文件：`rainfall_mcp_server.log`
- 支持控制台和文件双输出
- 调试模式使用 `--debug` 参数

### 网络配置
- Web 服务器端口：8081
- MCP 服务器使用 stdio 传输
- 支持局域网访问

### 数据格式要求
数据文件应包含以下列：
- `date`: 日期 (支持 "2024年1月1日" 或 "2024-01-01" 格式)
- `region`: 地区/站点名称
- `rainfall`: 降雨量 (mm)

## 故障排除

### 常见问题
1. **API 密钥问题**: 运行 `python configure_api.py` 配置
2. **数据文件未找到**: 检查 `data/` 目录中的 XLSX 文件
3. **端口占用**: 修改 `web_server.py` 中的端口配置
4. **编码问题**: 数据处理器支持多种中文编码自动检测

### 服务管理
- 停止服务：关闭终端窗口或使用 `Ctrl+C`
- 强制停止：`taskkill /F /IM python.exe`
- 检查服务状态：访问 http://localhost:8081