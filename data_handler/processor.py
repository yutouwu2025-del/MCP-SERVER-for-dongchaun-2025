"""
Data processor for rainfall data analysis and statistics
"""
import pandas as pd
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta


class RainfallDataProcessor:
    """Process rainfall data for analysis and statistics"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def calculate_basic_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic rainfall statistics"""
        if df.empty or 'rainfall' not in df.columns:
            return {}

        try:
            rainfall_col = pd.to_numeric(df['rainfall'], errors='coerce')
            valid_data = rainfall_col.dropna()

            if valid_data.empty:
                return {}

            stats = {
                'count': int(len(valid_data)),
                'sum': float(valid_data.sum()),
                'mean': float(valid_data.mean()),
                'median': float(valid_data.median()),
                'std': float(valid_data.std()),
                'min': float(valid_data.min()),
                'max': float(valid_data.max()),
                'q25': float(valid_data.quantile(0.25)),
                'q75': float(valid_data.quantile(0.75))
            }

            # 计算百分位数
            percentiles = [10, 90, 95, 99]
            for p in percentiles:
                stats[f'p{p}'] = float(valid_data.quantile(p/100))

            return stats

        except Exception as e:
            self.logger.error(f"Error calculating basic stats: {e}")
            return {}

    def analyze_by_region(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze rainfall data grouped by region"""
        if df.empty or 'region' not in df.columns or 'rainfall' not in df.columns:
            return {}

        try:
            region_stats = {}
            grouped = df.groupby('region')

            for region, group in grouped:
                rainfall_col = pd.to_numeric(group['rainfall'], errors='coerce')
                valid_data = rainfall_col.dropna()

                if not valid_data.empty:
                    region_stats[str(region)] = {
                        'count': int(len(valid_data)),
                        'total': float(valid_data.sum()),
                        'average': float(valid_data.mean()),
                        'max': float(valid_data.max()),
                        'min': float(valid_data.min()),
                        'std': float(valid_data.std())
                    }

            return region_stats

        except Exception as e:
            self.logger.error(f"Error analyzing by region: {e}")
            return {}

    def analyze_by_time_period(self, df: pd.DataFrame, period: str = 'month') -> Dict[str, Any]:
        """Analyze rainfall data by time period (month, season, year)"""
        if df.empty or 'date' not in df.columns or 'rainfall' not in df.columns:
            return {}

        try:
            # 转换日期列
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            df_with_dates = df.dropna(subset=['date_parsed'])

            if df_with_dates.empty:
                return {}

            rainfall_col = pd.to_numeric(df_with_dates['rainfall'], errors='coerce')
            df_with_dates = df_with_dates.assign(rainfall_numeric=rainfall_col)
            df_clean = df_with_dates.dropna(subset=['rainfall_numeric'])

            if df_clean.empty:
                return {}

            time_stats = {}

            if period == 'month':
                grouped = df_clean.groupby(df_clean['date_parsed'].dt.to_period('M'))
                for period_key, group in grouped:
                    time_stats[str(period_key)] = {
                        'total': float(group['rainfall_numeric'].sum()),
                        'average': float(group['rainfall_numeric'].mean()),
                        'count': int(len(group))
                    }

            elif period == 'year':
                grouped = df_clean.groupby(df_clean['date_parsed'].dt.year)
                for year, group in grouped:
                    time_stats[str(year)] = {
                        'total': float(group['rainfall_numeric'].sum()),
                        'average': float(group['rainfall_numeric'].mean()),
                        'count': int(len(group))
                    }

            elif period == 'season':
                df_clean['season'] = df_clean['date_parsed'].dt.month.map({
                    12: '冬季', 1: '冬季', 2: '冬季',
                    3: '春季', 4: '春季', 5: '春季',
                    6: '夏季', 7: '夏季', 8: '夏季',
                    9: '秋季', 10: '秋季', 11: '秋季'
                })
                grouped = df_clean.groupby('season')
                for season, group in grouped:
                    time_stats[season] = {
                        'total': float(group['rainfall_numeric'].sum()),
                        'average': float(group['rainfall_numeric'].mean()),
                        'count': int(len(group))
                    }

            return time_stats

        except Exception as e:
            self.logger.error(f"Error analyzing by time period: {e}")
            return {}

    def detect_extreme_events(self, df: pd.DataFrame, threshold_percentile: float = 95) -> List[Dict[str, Any]]:
        """Detect extreme rainfall events"""
        if df.empty or 'rainfall' not in df.columns:
            return []

        try:
            rainfall_col = pd.to_numeric(df['rainfall'], errors='coerce')
            valid_data = df[rainfall_col.notna()].copy()

            if valid_data.empty:
                return []

            # 计算阈值
            threshold = rainfall_col.quantile(threshold_percentile / 100)
            extreme_events = valid_data[rainfall_col >= threshold]

            events = []
            for idx, row in extreme_events.iterrows():
                event = {
                    'index': int(idx),
                    'rainfall': float(row['rainfall']),
                    'percentile': float((rainfall_col < row['rainfall']).mean() * 100)
                }

                # 添加日期信息（如果有）
                if 'date' in row:
                    event['date'] = str(row['date'])

                # 添加地区信息（如果有）
                if 'region' in row:
                    event['region'] = str(row['region'])

                events.append(event)

            # 按降雨量排序
            events.sort(key=lambda x: x['rainfall'], reverse=True)

            return events

        except Exception as e:
            self.logger.error(f"Error detecting extreme events: {e}")
            return []

    def calculate_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate rainfall trends over time"""
        if df.empty or 'date' not in df.columns or 'rainfall' not in df.columns:
            return {}

        try:
            # 转换数据类型
            df['date_parsed'] = pd.to_datetime(df['date'], errors='coerce')
            rainfall_col = pd.to_numeric(df['rainfall'], errors='coerce')

            df_clean = df.dropna(subset=['date_parsed', 'rainfall'])
            if df_clean.empty:
                return {}

            df_clean = df_clean.assign(rainfall_numeric=rainfall_col.loc[df_clean.index])

            # 按月份聚合
            monthly_data = df_clean.groupby(df_clean['date_parsed'].dt.to_period('M')).agg({
                'rainfall_numeric': ['sum', 'mean', 'count']
            }).reset_index()

            monthly_data.columns = ['month', 'total', 'average', 'count']
            monthly_data = monthly_data.sort_values('month')

            if len(monthly_data) < 2:
                return {'trend': 'insufficient_data'}

            # 计算简单趋势（线性回归斜率）
            x = range(len(monthly_data))
            y_total = monthly_data['total'].values
            y_avg = monthly_data['average'].values

            # 使用numpy风格的简单线性回归
            n = len(x)
            sum_x = sum(x)
            sum_y_total = sum(y_total)
            sum_xy_total = sum(xi * yi for xi, yi in zip(x, y_total))
            sum_x2 = sum(xi * xi for xi in x)

            # 总降雨量趋势
            slope_total = (n * sum_xy_total - sum_x * sum_y_total) / (n * sum_x2 - sum_x * sum_x)

            # 平均降雨量趋势
            sum_y_avg = sum(y_avg)
            sum_xy_avg = sum(xi * yi for xi, yi in zip(x, y_avg))
            slope_avg = (n * sum_xy_avg - sum_x * sum_y_avg) / (n * sum_x2 - sum_x * sum_x)

            trends = {
                'total_rainfall_trend': float(slope_total),
                'average_rainfall_trend': float(slope_avg),
                'trend_direction': 'increasing' if slope_total > 0 else 'decreasing' if slope_total < 0 else 'stable',
                'data_points': int(len(monthly_data)),
                'analysis_period': {
                    'start': str(monthly_data['month'].iloc[0]),
                    'end': str(monthly_data['month'].iloc[-1])
                }
            }

            return trends

        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
            return {'error': str(e)}

    def generate_summary_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive summary report"""
        report = {
            'data_overview': {
                'total_records': len(df),
                'columns': list(df.columns)
            },
            'basic_statistics': self.calculate_basic_stats(df),
            'regional_analysis': self.analyze_by_region(df),
            'monthly_analysis': self.analyze_by_time_period(df, 'month'),
            'seasonal_analysis': self.analyze_by_time_period(df, 'season'),
            'extreme_events': self.detect_extreme_events(df),
            'trends': self.calculate_trends(df)
        }

        return report