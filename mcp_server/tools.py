"""
MCP tools for rainfall data query and analysis
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from mcp.types import TextContent

from config.settings import settings
from data_handler.reader import RainfallDataReader
from data_handler.processor import RainfallDataProcessor
from ai_service.analyzer import get_analyzer


class RainfallTools:
    """Collection of MCP tools for rainfall data operations"""

    def __init__(self):
        self.data_reader = RainfallDataReader(settings.data_dir)
        self.data_processor = RainfallDataProcessor()
        self.logger = logging.getLogger(__name__)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get list of all available MCP tool definitions"""
        return [
            {
                "name": "query_rainfall",
                "description": "Query rainfall data from available datasets with optional filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the data file (without .xlsx extension)"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters for data query",
                            "properties": {
                                "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                                "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
                                "region": {"type": "string", "description": "Region name or pattern"},
                                "min_rainfall": {"type": "number", "description": "Minimum rainfall amount"},
                                "max_rainfall": {"type": "number", "description": "Maximum rainfall amount"}
                            }
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of records to return",
                            "default": 100
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "analyze_rainfall",
                "description": "Perform AI-powered analysis of rainfall data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the data file to analyze"
                        },
                        "question": {
                            "type": "string",
                            "description": "Specific question about the data (optional)"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["general", "trends", "summary", "question"],
                            "description": "Type of analysis to perform",
                            "default": "general"
                        },
                        "model_name": {
                            "type": "string",
                            "description": "AI model to use for analysis",
                            "default": "deepseek-chat"
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "rainfall_summary",
                "description": "Get statistical summary of rainfall data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the data file"
                        },
                        "include_ai_analysis": {
                            "type": "boolean",
                            "description": "Include AI-generated analysis",
                            "default": False
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "list_datasets",
                "description": "List all available rainfall datasets",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_summary": {
                            "type": "boolean",
                            "description": "Include basic summary for each dataset",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "extreme_events",
                "description": "Detect extreme rainfall events in the data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the data file"
                        },
                        "threshold_percentile": {
                            "type": "number",
                            "description": "Percentile threshold for extreme events (default: 95)",
                            "default": 95,
                            "minimum": 50,
                            "maximum": 99.9
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of events to return",
                            "default": 10
                        }
                    },
                    "required": ["filename"]
                }
            },
            {
                "name": "compare_periods",
                "description": "Compare rainfall data between different time periods",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Name of the data file"
                        },
                        "period1_start": {
                            "type": "string",
                            "description": "Start date of first period (YYYY-MM-DD)"
                        },
                        "period1_end": {
                            "type": "string",
                            "description": "End date of first period (YYYY-MM-DD)"
                        },
                        "period2_start": {
                            "type": "string",
                            "description": "Start date of second period (YYYY-MM-DD)"
                        },
                        "period2_end": {
                            "type": "string",
                            "description": "End date of second period (YYYY-MM-DD)"
                        },
                        "include_ai_analysis": {
                            "type": "boolean",
                            "description": "Include AI-powered comparison analysis",
                            "default": True
                        }
                    },
                    "required": ["filename", "period1_start", "period1_end", "period2_start", "period2_end"]
                }
            },
            {
                "name": "analyze_all_rainfall_data",
                "description": "Perform AI-powered analysis on all available rainfall data files combined",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Specific question about the combined data"
                        },
                        "analysis_type": {
                            "type": "string",
                            "enum": ["general", "trends", "summary", "comparison", "regional"],
                            "description": "Type of analysis to perform on all data",
                            "default": "general"
                        },
                        "model_name": {
                            "type": "string",
                            "description": "AI model to use for analysis",
                            "default": "deepseek-chat"
                        }
                    },
                    "required": []
                }
            }
        ]

    async def query_rainfall(self, filename: str, filters: Dict[str, Any] = None, limit: int = 100) -> List[TextContent]:
        """Query rainfall data with optional filters"""
        try:
            # 查询数据
            df = self.data_reader.query_data(filename, filters)

            if df.empty:
                return [TextContent(
                    type="text",
                    text=f"No data found for file '{filename}' with the specified filters."
                )]

            # 限制返回记录数
            total_matching = len(df)
            if len(df) > limit:
                df = df.head(limit)
                is_truncated = True
            else:
                is_truncated = False

            # 转换为JSON格式，处理日期序列化
            df_copy = df.copy()
            for col in df_copy.columns:
                if df_copy[col].dtype == 'datetime64[ns]':
                    df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
                elif 'datetime' in str(df_copy[col].dtype):
                    df_copy[col] = df_copy[col].astype(str)

            result_data = {
                "filename": filename,
                "filters_applied": filters or {},
                "returned_records": len(df_copy),
                "total_matching_records": total_matching,
                "is_truncated": is_truncated,
                "data": df_copy.to_dict('records')
            }

            return [TextContent(
                type="text",
                text=json.dumps(result_data, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            self.logger.error(f"Error querying rainfall data: {e}")
            return [TextContent(
                type="text",
                text=f"Error querying data: {str(e)}"
            )]

    async def analyze_rainfall(self, filename: str, question: str = None,
                             analysis_type: str = "general", model_name: str = "deepseek-chat") -> List[TextContent]:
        """Perform AI-powered analysis of rainfall data"""
        try:
            # 获取数据摘要
            data_summary = self.data_reader.get_data_summary(filename)
            if not data_summary:
                return [TextContent(
                    type="text",
                    text=f"No data found for file '{filename}'"
                )]

            # 获取处理后的统计数据
            df = self.data_reader.read_data_file(filename)
            if df is not None:
                detailed_summary = self.data_processor.generate_summary_report(df)
                data_summary.update(detailed_summary)

            # 使用AI进行分析
            async with get_analyzer(model_name) as analyzer:
                if analysis_type == "trends":
                    result = await analyzer.predict_trends(data_summary)
                elif analysis_type == "summary":
                    result = await analyzer.generate_summary_report(data_summary)
                elif analysis_type == "question" and question:
                    result = await analyzer.answer_question(data_summary, question)
                else:
                    result = await analyzer.analyze_data(data_summary, question)

            if result.get("success"):
                response_data = {
                    "success": True,
                    "analysis_type": analysis_type,
                    "model_used": model_name,
                    "filename": filename,
                    "analysis": result.get("analysis") or result.get("summary") or result.get("prediction"),
                    "data_overview": {
                        "total_records": data_summary.get("total_records", 0),
                        "date_range": data_summary.get("date_range"),
                        "regions": data_summary.get("regions", [])
                    }
                }

                return [TextContent(
                    type="text",
                    text=json.dumps(response_data, ensure_ascii=False, indent=2)
                )]
            else:
                error_response = {
                    "success": False,
                    "error": result.get('error', 'Unknown error'),
                    "analysis_type": analysis_type,
                    "filename": filename,
                    "model_used": model_name
                }
                return [TextContent(
                    type="text",
                    text=json.dumps(error_response, ensure_ascii=False, indent=2)
                )]

        except Exception as e:
            self.logger.error(f"Error analyzing rainfall data: {e}")
            error_response = {
                "success": False,
                "error": str(e),
                "analysis_type": analysis_type if 'analysis_type' in locals() else "general",
                "filename": filename,
                "model_used": model_name if 'model_name' in locals() else "deepseek-chat"
            }
            return [TextContent(
                type="text",
                text=json.dumps(error_response, ensure_ascii=False, indent=2)
            )]

    async def rainfall_summary(self, filename: str, include_ai_analysis: bool = False) -> List[TextContent]:
        """Get statistical summary of rainfall data"""
        try:
            # 获取数据摘要
            data_summary = self.data_reader.get_data_summary(filename)
            if not data_summary:
                return [TextContent(
                    type="text",
                    text=f"No data found for file '{filename}'"
                )]

            # 获取详细统计
            df = self.data_reader.read_data_file(filename)
            if df is not None:
                detailed_stats = self.data_processor.generate_summary_report(df)
                data_summary.update(detailed_stats)

            # 如果需要AI分析
            ai_analysis = None
            if include_ai_analysis:
                try:
                    async with get_analyzer() as analyzer:
                        ai_result = await analyzer.generate_summary_report(data_summary)
                        if ai_result.get("success"):
                            ai_analysis = ai_result.get("summary")
                except Exception as e:
                    self.logger.warning(f"AI analysis failed: {e}")

            result_data = {
                "filename": filename,
                "summary": data_summary,
                "ai_analysis": ai_analysis
            }

            return [TextContent(
                type="text",
                text=json.dumps(result_data, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return [TextContent(
                type="text",
                text=f"Error generating summary: {str(e)}"
            )]

    async def list_datasets(self, include_summary: bool = False) -> List[TextContent]:
        """List all available rainfall datasets"""
        try:
            available_files = self.data_reader.get_available_files()

            if not available_files:
                return [TextContent(
                    type="text",
                    text="No rainfall datasets found in the data directory."
                )]

            datasets_info = {
                "available_datasets": len(available_files),
                "datasets": []
            }

            for filename in available_files:
                dataset_info = {"filename": filename}

                if include_summary:
                    summary = self.data_reader.get_data_summary(filename)
                    dataset_info["summary"] = summary

                datasets_info["datasets"].append(dataset_info)

            return [TextContent(
                type="text",
                text=json.dumps(datasets_info, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            self.logger.error(f"Error listing datasets: {e}")
            return [TextContent(
                type="text",
                text=f"Error listing datasets: {str(e)}"
            )]

    async def extreme_events(self, filename: str, threshold_percentile: float = 95, limit: int = 10) -> List[TextContent]:
        """Detect extreme rainfall events"""
        try:
            df = self.data_reader.read_data_file(filename)
            if df is None or df.empty:
                return [TextContent(
                    type="text",
                    text=f"No data found for file '{filename}'"
                )]

            events = self.data_processor.detect_extreme_events(df, threshold_percentile)

            if not events:
                return [TextContent(
                    type="text",
                    text=f"No extreme events found with threshold {threshold_percentile}th percentile"
                )]

            # 限制返回数量
            limited_events = events[:limit]

            result_data = {
                "filename": filename,
                "threshold_percentile": threshold_percentile,
                "total_extreme_events": len(events),
                "events_returned": len(limited_events),
                "extreme_events": limited_events
            }

            return [TextContent(
                type="text",
                text=json.dumps(result_data, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            self.logger.error(f"Error detecting extreme events: {e}")
            return [TextContent(
                type="text",
                text=f"Error detecting extreme events: {str(e)}"
            )]

    async def compare_periods(self, filename: str, period1_start: str, period1_end: str,
                            period2_start: str, period2_end: str, include_ai_analysis: bool = True) -> List[TextContent]:
        """Compare rainfall data between different time periods"""
        try:
            # 查询两个时期的数据
            filters1 = {"start_date": period1_start, "end_date": period1_end}
            filters2 = {"start_date": period2_start, "end_date": period2_end}

            df1 = self.data_reader.query_data(filename, filters1)
            df2 = self.data_reader.query_data(filename, filters2)

            if df1.empty or df2.empty:
                return [TextContent(
                    type="text",
                    text="One or both periods contain no data"
                )]

            # 生成两个时期的统计数据
            stats1 = self.data_processor.generate_summary_report(df1)
            stats2 = self.data_processor.generate_summary_report(df2)

            comparison_data = {
                "filename": filename,
                "period1": {
                    "range": f"{period1_start} to {period1_end}",
                    "statistics": stats1
                },
                "period2": {
                    "range": f"{period2_start} to {period2_end}",
                    "statistics": stats2
                }
            }

            # 如果需要AI分析
            if include_ai_analysis:
                try:
                    async with get_analyzer() as analyzer:
                        ai_result = await analyzer.compare_periods(
                            stats1, stats2,
                            f"Period 1 ({period1_start} to {period1_end})",
                            f"Period 2 ({period2_start} to {period2_end})"
                        )
                        if ai_result.get("success"):
                            comparison_data["ai_comparison"] = ai_result.get("comparison")
                except Exception as e:
                    self.logger.warning(f"AI comparison failed: {e}")

            return [TextContent(
                type="text",
                text=json.dumps(comparison_data, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            self.logger.error(f"Error comparing periods: {e}")
            return [TextContent(
                type="text",
                text=f"Error comparing periods: {str(e)}"
            )]

    async def analyze_all_rainfall_data(self, question: str = None,
                                      analysis_type: str = "general",
                                      model_name: str = "deepseek-chat") -> List[TextContent]:
        """Perform AI-powered analysis on all available rainfall data files combined"""
        try:
            # 获取所有数据的综合摘要
            combined_summary = self.data_reader.get_combined_data_summary()

            if not combined_summary or combined_summary.get('total_files', 0) == 0:
                return [TextContent(
                    type="text",
                    text="No data files found for analysis"
                )]

            # 使用AI进行分析
            async with get_analyzer(model_name) as analyzer:
                if analysis_type == "trends":
                    result = await analyzer.predict_trends(combined_summary)
                elif analysis_type == "summary":
                    result = await analyzer.generate_summary_report(combined_summary)
                elif analysis_type == "regional":
                    # 构建区域分析的问题
                    regional_question = question or "请分析不同地区的降雨模式和差异"
                    result = await analyzer.analyze_data(combined_summary, regional_question)
                elif analysis_type == "comparison":
                    # 构建比较分析的问题
                    comparison_question = question or "请比较分析各个监测站点的降雨数据特征和差异"
                    result = await analyzer.analyze_data(combined_summary, comparison_question)
                else:
                    # 通用分析
                    general_question = question or "请对所有降雨监测数据进行综合分析，包括整体趋势、地区差异、季节性变化等"
                    result = await analyzer.analyze_data(combined_summary, general_question)

            if result.get("success"):
                response_data = {
                    "success": True,
                    "analysis_type": analysis_type,
                    "model_used": model_name,
                    "data_scope": "all_files",
                    "analysis": result.get("analysis") or result.get("summary") or result.get("prediction"),
                    "data_overview": {
                        "total_files": combined_summary.get("total_files", 0),
                        "total_records": combined_summary.get("total_records", 0),
                        "date_range": combined_summary.get("date_range"),
                        "regions": combined_summary.get("all_regions", []),
                        "rainfall_stats": combined_summary.get("rainfall_stats", {}),
                        "file_summaries": combined_summary.get("file_summaries", {})
                    }
                }
            else:
                response_data = {
                    "success": False,
                    "error": result.get("error", "Analysis failed"),
                    "data_scope": "all_files",
                    "total_files": combined_summary.get("total_files", 0)
                }

            return [TextContent(
                type="text",
                text=json.dumps(response_data, ensure_ascii=False, indent=2)
            )]

        except Exception as e:
            self.logger.error(f"Error in multi-file analysis: {e}")
            return [TextContent(
                type="text",
                text=f"Error analyzing all rainfall data: {str(e)}"
            )]


# Global tools instance
rainfall_tools = RainfallTools()