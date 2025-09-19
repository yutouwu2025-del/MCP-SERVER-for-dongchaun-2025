# 🌧️ 中科院东川站降雨量分析服务平台

> 基于 Model Context Protocol (MCP) 的智能降雨量数据查询与分析系统

[![MCP Version](https://img.shields.io/badge/MCP-0.5.2-blue.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![AI Model](https://img.shields.io/badge/AI-DeepSeek-orange.svg)](https://www.deepseek.com)

**中国科学院东川泥石流观测研究站**降雨量数据查询和分析服务器，集成 DeepSeek AI 模型进行智能数据分析，提供现代化的Web监控界面。

---

## 📋 目录

- [🚀 快速启动](#-快速启动)
- [🛠️ 技术栈](#️-技术栈)
- [🏗️ 系统架构](#️-系统架构)
- [📁 项目结构](#-项目结构)
- [🎯 MCP协议详解](#-mcp协议详解)
- [✨ 功能特性](#-功能特性)
- [🔧 系统要求](#-系统要求)
- [⚙️ 安装配置](#️-安装配置)
- [🎮 使用方法](#-使用方法)
- [🔧 MCP工具列表](#-mcp工具列表)
- [🌐 Web API接口](#-web-api接口)
- [🔍 运行机制](#-运行机制)
- [🔒 安全说明](#-安全说明)
- [🚨 故障排除](#-故障排除)

---

## 🚀 快速启动

### 一键启动（推荐）
```bash
# Windows环境（推荐）
start_all.bat

# 跨平台Python启动
python web_server.py
```

### 访问界面
- **本地访问**: http://localhost:8081
- **局域网访问**: http://[您的IP地址]:8081

---

## 🛠️ 技术栈

### 核心技术
| 技术组件 | 版本 | 用途 |
|---------|------|------|
| **Python** | 3.8+ | 主要开发语言 |
| **MCP Protocol** | 0.5.2 | AI模型与外部工具连接协议 |
| **DeepSeek AI** | Latest | 智能数据分析模型 |
| **pandas** | 1.5.0+ | 数据处理与分析 |
| **asyncio** | 3.4.3+ | 异步编程框架 |

### Web技术栈
| 技术 | 用途 |
|------|------|
| **HTTP Server** | 基于Python内置服务器 |
| **HTML5/CSS3** | 现代化响应式界面 |
| **JavaScript ES6** | 交互逻辑与API调用 |
| **JSON-RPC 2.0** | MCP通信协议 |

### 数据处理
| 组件 | 支持格式 | 功能 |
|------|---------|------|
| **pandas** | CSV, TXT, XLSX | 数据读取与处理 |
| **openpyxl** | Excel文件 | 电子表格解析 |
| **多编码支持** | UTF-8, GBK, GB2312 | 中文数据处理 |

---

## 🏗️ 系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层                                │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   Web浏览器界面    │   MCP客户端      │      API调用接口              │
│   (8081端口)     │  (Claude等)     │    (HTTP REST)              │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                      Web服务器层                                 │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   HTTP Handler   │   API路由       │      CORS处理                │
│   异步请求处理     │   JSON响应      │      错误处理                │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                       MCP服务层                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   MCP协议处理    │   工具管理       │      消息路由                │
│   JSON-RPC 2.0  │   权限控制       │      状态管理                │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                       业务逻辑层                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   数据查询工具    │   AI分析工具     │      统计分析工具             │
│   降雨数据处理    │   智能问答       │      极端事件检测             │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                       数据访问层                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   文件读取器     │   数据处理器     │      缓存管理                │
│   多格式支持     │   中文日期解析   │      配置管理                │
└─────────────────┴─────────────────┴─────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────────┐
│                       外部集成层                                  │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   DeepSeek API   │   本地数据文件   │      配置文件                │
│   HTTPS调用      │   CSV/TXT/XLSX  │      JSON/TXT               │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

### 数据流转图
```
用户请求 → Web界面 → HTTP API → MCP工具 → 数据处理 → AI分析 → 结果返回
    ↓                                   ↓            ↓
浏览器显示 ← JSON响应 ← 格式化输出 ← 智能分析 ← 数据读取
```

---

## 📁 项目结构

```
MCP SERVER/
├── 🚀 启动文件
│   ├── start_all.bat              # 一键启动脚本（推荐）
│   ├── start_server.py            # MCP服务器启动
│   └── web_server.py              # Web服务器主程序
│
├── 🌐 用户界面
│   └── web_interface.html         # 现代化Web监控界面
│
├── 🔧 核心模块
│   ├── config/                    # 配置管理模块
│   │   ├── __init__.py
│   │   ├── settings.py            # 主配置文件
│   │   └── models.py              # AI模型配置
│   │
│   ├── data_handler/              # 数据处理模块
│   │   ├── __init__.py
│   │   ├── reader.py              # 多格式数据读取器
│   │   └── processor.py           # 数据分析处理器
│   │
│   ├── ai_service/                # AI服务模块
│   │   ├── __init__.py
│   │   ├── deepseek.py            # DeepSeek客户端
│   │   └── analyzer.py            # 智能分析器
│   │
│   └── mcp_server/                # MCP服务器模块
│       ├── __init__.py
│       └── tools.py               # MCP工具实现
│
├── 📊 数据目录
│   └── data/                      # 降雨量数据文件
│       ├── *.txt                  # 文本数据文件
│       ├── *.csv                  # CSV数据文件
│       └── *.xlsx                 # Excel数据文件
│
├── ⚙️ 配置文件
│   ├── requirements.txt           # Python依赖包
│   ├── deepseekkey.txt           # DeepSeek API配置
│   ├── main.py                   # 程序入口点
│   └── configure_api.py          # API配置助手
│
└── 📖 文档
    └── README.md                 # 项目文档（本文件）
```

---

## 🎯 MCP协议详解

### 什么是MCP？

**Model Context Protocol (MCP)** 是Anthropic开发的开放标准协议，用于AI模型与外部工具和数据源的安全连接。

### 协议架构
```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│                 │ ◄────────────────► │                 │
│   MCP Client    │    JSON-RPC 2.0    │   MCP Server    │
│  (AI Assistant) │     over stdio     │ (Tools & Data)  │
│                 │                    │                 │
└─────────────────┘                    └─────────────────┘
```

### MCP连接流程

#### 1. 服务器启动
```bash
python start_server.py
# 服务器监听 stdio，等待客户端连接
```

#### 2. 协议握手
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {"listChanged": true}
    },
    "clientInfo": {
      "name": "claude-desktop",
      "version": "0.5.0"
    }
  }
}
```

#### 3. 工具发现
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "query_rainfall",
        "description": "查询降雨量数据",
        "inputSchema": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "filters": {"type": "object"},
            "limit": {"type": "integer"}
          }
        }
      }
    ]
  }
}
```

#### 4. 工具调用
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "query_rainfall",
    "arguments": {
      "filename": "Dabaini",
      "limit": 10
    }
  }
}
```

### MCP客户端配置

#### Claude Desktop配置
在 `%APPDATA%\\Claude\\claude_desktop_config.json` 中：
```json
{
  "mcpServers": {
    "rainfall-query": {
      "command": "python",
      "args": ["C:\\\\path\\\\to\\\\your\\\\project\\\\start_server.py"],
      "cwd": "C:\\\\path\\\\to\\\\your\\\\project"
    }
  }
}
```

---

## ✨ 功能特性

### 🌐 现代化Web界面
- 📊 **实时状态监控**: MCP Server、DeepSeek AI、数据文件、MCP连接状态
- 🎨 **美观动画效果**: 悬停动画、状态指示器、渐变背景
- 📱 **响应式设计**: 支持桌面和移动设备
- 🔧 **一键操作**: 浏览器中直接测试所有功能
- 🌍 **局域网访问**: 支持多设备同时使用

### ⚙️ MCP服务器核心功能
- 📊 **智能数据查询**: 支持多种过滤条件的降雨量数据查询
- 🤖 **AI深度分析**: DeepSeek模型进行智能数据分析和模式识别
- 📈 **统计分析**: 自动生成详细的统计报告和数据摘要
- ⚡ **异常检测**: 智能识别极端降雨事件和异常模式
- 🔄 **时期比较**: 对比不同时间段的降雨模式和趋势
- 🔗 **标准协议**: 完整的MCP 2024-11-05协议实现

### 📊 数据处理能力
- 🗂️ **多格式支持**: CSV、TXT、XLSX文件格式
- 🌏 **多编码处理**: UTF-8、GBK、GB2312中文编码支持
- 📅 **智能日期解析**: 自动识别中文日期格式（如"2024年1月1日"）
- 🧮 **统计计算**: 均值、中位数、极值、标准差等统计指标
- 🔍 **数据过滤**: 按日期范围、地区、降雨量范围灵活过滤

---

## 🔧 系统要求

### 硬件要求
- **CPU**: 2核心以上处理器
- **内存**: 最小2GB，推荐4GB+
- **存储**: 至少500MB可用空间
- **网络**: 稳定的网络连接（用于AI模型API调用）

### 软件要求
- **操作系统**: Windows 10+, Linux, macOS
- **Python**: 3.8或更高版本
- **浏览器**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+

### 网络要求
- **出站连接**: 访问DeepSeek API (https://api.deepseek.com)
- **入站连接**: 8081端口（Web界面访问）
- **带宽**: 最小1Mbps上下行速度

---

## ⚙️ 安装配置

### 1. 环境准备
```bash
# 检查Python版本
python --version  # 需要3.8+

# 克隆或下载项目到本地
cd "C:\\Users\\Administrator\\Desktop\\MCP SERVER"
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置DeepSeek API密钥

#### 方法一：使用配置助手（推荐）
```bash
python configure_api.py
# 按提示输入API密钥
```

#### 方法二：手动编辑配置文件
编辑 `deepseekkey.txt` 文件：
```ini
# DeepSeek API 配置文件
base_url: https://api.deepseek.com
api_token: sk-your-deepseek-api-key-here  # 替换为实际的API密钥
timeout: 60
max_retries: 3
```

#### 获取API密钥步骤：
1. 访问 [DeepSeek平台](https://platform.deepseek.com)
2. 注册/登录账户
3. 进入API密钥管理页面
4. 创建新的API密钥
5. 复制密钥（格式：sk-xxxxxxxxxx）

### 4. 准备数据文件
将降雨量数据文件放入 `data/` 目录，支持格式：
- **.xlsx** 文件（Excel电子表格）
- **.txt** 文件（制表符分隔）
- **.csv** 文件（逗号分隔）

#### 数据文件格式要求
数据文件应包含以下列：
| 列名 | 描述 | 示例 |
|------|------|------|
| date | 日期 | 2024年1月1日 或 2024-01-01 |
| region | 地区/站点 | 东川站 |
| rainfall | 降雨量(mm) | 15.5 |

---

## 🎮 使用方法

### 方式一：Web界面操作（推荐）

#### 1. 启动服务
```bash
# 一键启动（推荐）
start_all.bat

# 或手动启动Web服务器
python web_server.py
```

#### 2. 访问界面
- **本地**: http://localhost:8081
- **局域网**: http://[您的IP地址]:8081

#### 3. 功能使用
1. **状态监控** - 页面加载时自动检查所有状态
2. **基本数据查询** - 设置文件、记录数进行查询
3. **AI智能分析** - 输入问题获得智能分析结果
4. **统计摘要** - 生成全面的数据统计报告
5. **极端事件检测** - 识别异常强降雨事件
6. **系统控制** - 检查服务器状态、测试AI连接

### 方式二：MCP客户端连接

#### 1. 启动MCP服务器
```bash
python start_server.py
```

#### 2. 配置MCP客户端
在Claude Desktop或其他MCP客户端中添加服务器配置

#### 3. 使用MCP工具
客户端会自动发现并可以调用7个可用工具

---

## 🔧 MCP工具列表

### 1. `query_rainfall` - 数据查询
**功能**: 查询降雨数据，支持多种过滤条件
```json
{
  "filename": "Dabaini",
  "filters": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "min_rainfall": 0,
    "max_rainfall": 100
  },
  "limit": 100
}
```

### 2. `analyze_rainfall` - AI数据分析
**功能**: 使用DeepSeek AI进行智能数据分析
```json
{
  "filename": "Dabaini",
  "question": "这个地区的降雨模式如何？分析季节性变化趋势",
  "analysis_type": "general"
}
```

### 3. `rainfall_summary` - 统计摘要
**功能**: 生成全面的数据统计报告
```json
{
  "filename": "Dabaini",
  "include_ai_analysis": true
}
```

### 4. `list_datasets` - 数据集列表
**功能**: 列出所有可用的降雨数据集
```json
{
  "include_summary": true
}
```

### 5. `extreme_events` - 极端事件检测
**功能**: 检测和分析极端降雨事件
```json
{
  "filename": "Dabaini",
  "threshold_percentile": 95,
  "limit": 10
}
```

### 6. `compare_periods` - 时期比较分析
**功能**: 对比不同时间段的降雨模式
```json
{
  "filename": "Dabaini",
  "period1_start": "2024-01-01",
  "period1_end": "2024-06-30",
  "period2_start": "2024-07-01",
  "period2_end": "2024-12-31",
  "include_ai_analysis": true
}
```

### 7. `analyze_all_rainfall_data` - 全数据综合分析
**功能**: 对所有数据文件进行综合分析
```json
{
  "question": "分析所有监测站点的降雨特征和地区差异",
  "analysis_type": "regional"
}
```

---

## 🌐 Web API接口

### 基础信息
- **Base URL**: http://localhost:8081
- **Content-Type**: application/json
- **Method**: POST

### API端点列表

#### 1. `/api/status` - 系统状态检查
**请求**:
```http
POST /api/status
Content-Type: application/json
```

**响应**:
```json
{
  "server": {
    "running": true,
    "version": "1.0.0",
    "port": 8081
  },
  "ai": {
    "configured": true,
    "provider": "DeepSeek",
    "model": "deepseek-chat"
  },
  "data": {
    "files_found": 7,
    "files": ["Dabaini", "Lijiayakou", "..."],
    "total_records": 2555
  },
  "mcp": {
    "tools_available": true,
    "tools_count": 7,
    "status": "ready"
  }
}
```

#### 2. `/api/query` - 数据查询
**请求**:
```http
POST /api/query
Content-Type: application/json

{
  "filename": "Dabaini",
  "limit": 10,
  "filters": {}
}
```

**响应**:
```json
{
  "filename": "Dabaini",
  "returned_records": 10,
  "total_matching_records": 364,
  "is_truncated": true,
  "data": [
    {
      "date": "2024-01-01",
      "region": "东川站",
      "rainfall": 0.0
    }
  ]
}
```

#### 3. `/api/analyze` - AI分析
**请求**:
```http
POST /api/analyze
Content-Type: application/json

{
  "filename": "Dabaini",
  "question": "分析降雨模式"
}
```

#### 4. `/api/summary` - 统计摘要
**请求**:
```http
POST /api/summary
Content-Type: application/json

{
  "filename": "Dabaini",
  "include_ai_analysis": false
}
```

#### 5. `/api/extreme` - 极端事件
**请求**:
```http
POST /api/extreme
Content-Type: application/json

{
  "filename": "Dabaini",
  "threshold_percentile": 95,
  "limit": 10
}
```

#### 6. `/api/test-deepseek` - AI连接测试
**请求**:
```http
POST /api/test-deepseek
Content-Type: application/json
```

---

## 🔍 运行机制

### 系统启动流程
```
1. 启动脚本执行
   ↓
2. 加载配置文件
   ↓
3. 初始化数据读取器
   ↓
4. 启动Web服务器 (8081端口)
   ↓
5. 加载MCP工具定义
   ↓
6. 建立AI服务连接
   ↓
7. 系统就绪，等待请求
```

### 请求处理流程
```
用户请求 → HTTP路由 → 参数验证 → MCP工具调用 → 数据处理
    ↓
结果返回 ← JSON格式化 ← 错误处理 ← AI分析 ← 数据查询
```

### 数据处理机制

#### 1. 数据读取流程
```python
# 1. 文件格式检测
supported_formats = ['.xlsx', '.txt', '.csv']

# 2. 编码自动检测
encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']

# 3. 数据标准化
columns = ['date', 'region', 'rainfall']

# 4. 日期解析
chinese_date_pattern = r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?'
```

#### 2. 缓存机制
- **内存缓存**: 已读取的数据文件缓存在内存中
- **懒加载**: 仅在需要时读取数据文件
- **缓存清理**: 支持手动清理缓存释放内存

#### 3. 异步处理
```python
# Web服务器使用异步事件循环
async def handle_request():
    result = await mcp_tool.process()
    return format_response(result)
```

### AI分析流程
```
用户问题 → 数据摘要生成 → DeepSeek API调用 → 结果解析 → 格式化输出
    ↓
上下文构建 → 提示词优化 → 模型推理 → 智能分析 → 结构化返回
```

---

## 🔒 安全说明

### MCP安全特性
- **沙箱运行**: 服务器运行在受限环境中
- **权限控制**: 客户端需要明确授权工具使用
- **数据隔离**: 敏感数据不会发送到外部服务
- **输入验证**: 严格的参数校验和清理

### API安全
- **密钥保护**: API密钥仅在本地配置文件中存储
- **请求限制**: 内置超时和重试机制
- **错误处理**: 不会泄露敏感的错误信息
- **CORS配置**: 适当的跨域资源共享设置

### 数据安全
- **本地处理**: 降雨数据仅在本地系统中处理
- **加密传输**: 与AI服务的通信使用HTTPS加密
- **访问控制**: 仅授权用户可访问系统功能

---

## 🚨 故障排除

### 常见问题

#### 1. 服务器无法启动
**症状**: Python脚本运行失败
```bash
# 解决方案
# 检查Python版本
python --version

# 检查依赖安装
pip list | grep mcp

# 重新安装依赖
pip install -r requirements.txt
```

#### 2. Web界面无法访问
**症状**: 浏览器显示连接错误
```bash
# 解决方案
# 检查端口占用
netstat -ano | findstr :8081

# 检查防火墙设置
# Windows: 控制面板 → 系统和安全 → Windows Defender防火墙

# 尝试其他端口
python web_server.py --port 8082
```

#### 3. AI分析功能失效
**症状**: AI分析返回错误或无响应
```bash
# 解决方案
# 检查API密钥配置
python configure_api.py

# 测试网络连接
curl -I https://api.deepseek.com

# 查看详细错误日志
tail -f *.log
```

#### 4. 数据文件读取失败
**症状**: 查询返回"No data found"
```bash
# 解决方案
# 检查数据文件格式
ls -la data/

# 验证文件编码
file data/*.txt

# 检查文件权限
chmod 644 data/*.txt
```

#### 5. MCP连接问题
**症状**: MCP客户端无法发现工具
```bash
# 解决方案
# 验证MCP服务器启动
python start_server.py --debug

# 检查客户端配置
# 确认JSON配置文件语法正确

# 重启MCP服务
# 关闭并重新启动MCP服务器
```

### 调试工具

#### 1. 日志查看
```bash
# Web服务器日志
python web_server.py --verbose

# MCP服务器调试
python start_server.py --debug

# 系统日志（Windows）
eventvwr.msc
```

#### 2. 网络测试
```bash
# 测试Web服务
curl -X POST http://localhost:8081/api/status

# 测试AI服务连接
curl -X POST http://localhost:8081/api/test-deepseek

# 端口连通性测试
telnet localhost 8081
```

#### 3. 浏览器调试
- 按 **F12** 打开开发者工具
- 查看 **Console** 标签页的错误信息
- 检查 **Network** 标签页的API请求和响应
- 监控 **Performance** 标签页的性能问题

### 性能优化

#### 1. 数据处理优化
```python
# 启用数据缓存
reader.cache_enabled = True

# 调整查询限制
query_limit = min(requested_limit, 1000)

# 异步文件读取
async def read_large_file():
    chunks = await file.read_chunks()
```

#### 2. Web服务优化
```python
# 启用HTTP缓存
response.headers['Cache-Control'] = 'max-age=300'

# 压缩响应内容
response.headers['Content-Encoding'] = 'gzip'

# 限制并发连接
server.max_connections = 100
```

---

## 📚 技术文档

### 开发指南
如需扩展系统功能，请参考以下指南：

#### 添加新的MCP工具
1. 在 `mcp_server/tools.py` 中定义新工具
2. 实现工具逻辑和参数验证
3. 添加到工具列表和路由
4. 更新文档和测试用例

#### 集成新的AI模型
1. 在 `ai_service/` 中添加新的客户端
2. 在 `config/models.py` 中配置模型参数
3. 更新分析器以支持新模型
4. 测试新模型的功能和性能

#### 扩展数据格式支持
1. 在 `data_handler/reader.py` 中添加新格式解析
2. 更新数据处理器以处理新字段
3. 修改前端界面以显示新数据类型
4. 添加相应的测试用例

---

## 📈 更新日志

### v1.0.0 (2025-09-17)
- ✨ 首个正式版本发布
- 🎯 完整的MCP 2024-11-05协议支持
- 🌐 现代化Web监控界面
- 🤖 集成DeepSeek AI智能分析
- 📊 支持多格式数据文件处理
- 🔧 一键启动脚本和配置助手

---

## 🤝 贡献指南

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd mcp-rainfall-server

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\\Scripts\\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 如果存在

# 运行测试
python -m pytest tests/
```

### 代码贡献流程
1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 Python代码风格
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 确保所有测试通过

---

## 📄 许可证

本项目仅供学习和研究使用。

---

## 📞 支持与联系

### 技术支持
- **作者**: wuy@imde.ac.cn
- **机构**: 中国科学院东川泥石流观测研究站
- **创建日期**: 2025年9月17日

### 问题反馈
如有问题，请：
1. 查看本文档的故障排除部分
2. 检查项目日志文件
3. 在GitHub提交Issue（如果有代码仓库）
4. 发送邮件至技术支持邮箱

### 功能建议
欢迎提出改进建议和新功能需求：
- 通过邮件联系开发团队
- 在项目仓库提交Feature Request
- 参与项目讨论和开发

---

## 🎉 快速开始示例

### 1. 一键启动系统
```bash
# Windows环境（推荐）
start_all.bat

# 跨平台启动
python web_server.py
```

### 2. 访问Web界面
打开浏览器访问：http://localhost:8081

### 3. 验证系统状态
页面将自动显示：
- 🟢 **MCP Server状态**: 运行中
- 🟢 **DeepSeek AI状态**: API已配置
- 🟢 **数据文件状态**: 找到7个数据文件
- 🟢 **MCP服务状态**: 7个工具可用

### 4. 体验核心功能
1. **基本数据查询** - 查看降雨量原始数据
2. **AI智能分析** - 提问"分析这个地区的降雨特征"
3. **统计摘要** - 生成全面的统计报告
4. **极端事件检测** - 识别异常强降雨事件

🎯 **现在您已拥有一个功能完整、技术先进的降雨量数据分析平台！**

---

*最后更新：2025年9月17日*