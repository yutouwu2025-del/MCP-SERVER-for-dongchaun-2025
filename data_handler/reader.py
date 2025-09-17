"""
Data reader for rainfall Excel files
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import re


class RainfallDataReader:
    """Reader for rainfall Excel data files"""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.cache: Dict[str, pd.DataFrame] = {}
        self.logger = logging.getLogger(__name__)

    def _parse_chinese_date(self, date_series: pd.Series) -> pd.Series:
        """Parse Chinese date format like '2024年1月1日' to datetime"""
        def parse_single_date(date_str):
            if pd.isna(date_str):
                return pd.NaT

            try:
                # 尝试标准格式解析
                return pd.to_datetime(date_str, format='%Y-%m-%d', errors='raise')
            except:
                pass

            try:
                # 尝试中文格式解析 '2024年1月1日'
                date_str = str(date_str).strip()
                match = re.match(r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?', date_str)
                if match:
                    year, month, day = match.groups()
                    return pd.Timestamp(int(year), int(month), int(day))
            except:
                pass

            try:
                # 最后尝试pandas自动解析（但会产生警告）
                return pd.to_datetime(date_str, errors='coerce')
            except:
                return pd.NaT

        return date_series.apply(parse_single_date)

    def get_available_files(self) -> List[str]:
        """Get list of available data files (Excel, TXT, CSV)"""
        data_files = []
        # 支持多种文件格式
        for pattern in ["*.xlsx", "*.txt", "*.csv"]:
            for file_path in self.data_dir.glob(pattern):
                if not file_path.name.startswith('~'):  # 跳过临时文件
                    data_files.append(file_path.stem)
        return list(set(data_files))  # 去重

    def read_data_file(self, filename: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Read data file (Excel, TXT, or CSV) and return DataFrame"""
        if use_cache and filename in self.cache:
            return self.cache[filename]

        # 尝试不同的文件扩展名
        possible_extensions = ['.xlsx', '.txt', '.csv']
        file_path = None

        for ext in possible_extensions:
            test_path = self.data_dir / f"{filename}{ext}"
            if test_path.exists():
                file_path = test_path
                break

        if file_path is None:
            self.logger.error(f"File not found: {filename} (tried extensions: {possible_extensions})")
            return None

        try:
            # 根据文件扩展名选择读取方法
            if file_path.suffix.lower() == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_path.suffix.lower() in ['.txt', '.csv']:
                # 尝试多种编码读取文本文件
                encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'latin-1']
                df = None

                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, sep='\t', encoding=encoding, on_bad_lines='skip')
                        self.logger.info(f"Successfully read {file_path} with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        self.logger.warning(f"Failed to read with encoding {encoding}: {e}")
                        continue

                if df is None:
                    self.logger.error(f"Failed to read {file_path} with any encoding")
                    return None
            else:
                self.logger.error(f"Unsupported file format: {file_path.suffix}")
                return None

            # 数据清理：删除空行和空列
            df = df.dropna(how='all').dropna(axis=1, how='all')

            # 尝试标准化列名
            if len(df.columns) >= 3:
                # 假设前三列是：日期、地区、降雨量
                df.columns = df.columns.astype(str)
                new_columns = []
                for i, col in enumerate(df.columns):
                    if i == 0:
                        new_columns.append('date')
                    elif i == 1:
                        new_columns.append('region')
                    elif i == 2:
                        new_columns.append('rainfall')
                    else:
                        new_columns.append(col)
                df.columns = new_columns

            # 缓存数据
            if use_cache:
                self.cache[filename] = df

            self.logger.info(f"Successfully loaded {filename}{file_path.suffix} with {len(df)} records")
            return df

        except Exception as e:
            self.logger.error(f"Error reading {filename}: {e}")
            return None

    def read_excel_file(self, filename: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Read Excel file and return DataFrame - kept for backward compatibility"""
        return self.read_data_file(filename, use_cache)

    def get_data_summary(self, filename: str) -> Dict[str, Any]:
        """Get summary information about the data file"""
        df = self.read_data_file(filename)
        if df is None:
            return {}

        summary = {
            'filename': filename,
            'total_records': len(df),
            'columns': list(df.columns),
            'date_range': None,
            'regions': [],
            'rainfall_stats': {}
        }

        try:
            # 尝试分析日期范围
            if 'date' in df.columns:
                date_col = self._parse_chinese_date(df['date'])
                valid_dates = date_col.dropna()
                if not valid_dates.empty:
                    summary['date_range'] = {
                        'start': valid_dates.min().strftime('%Y-%m-%d'),
                        'end': valid_dates.max().strftime('%Y-%m-%d')
                    }

            # 分析地区信息
            if 'region' in df.columns:
                regions = df['region'].dropna().unique().tolist()
                summary['regions'] = regions

            # 分析降雨量统计
            if 'rainfall' in df.columns:
                rainfall_col = pd.to_numeric(df['rainfall'], errors='coerce')
                valid_rainfall = rainfall_col.dropna()
                if not valid_rainfall.empty:
                    summary['rainfall_stats'] = {
                        'min': float(valid_rainfall.min()),
                        'max': float(valid_rainfall.max()),
                        'mean': float(valid_rainfall.mean()),
                        'median': float(valid_rainfall.median()),
                        'total': float(valid_rainfall.sum())
                    }

        except Exception as e:
            self.logger.warning(f"Error generating summary for {filename}: {e}")

        return summary

    def query_data(self, filename: str, filters: Dict[str, Any] = None) -> pd.DataFrame:
        """Query data with optional filters"""
        df = self.read_data_file(filename)
        if df is None:
            return pd.DataFrame()

        if not filters:
            return df

        filtered_df = df.copy()

        try:
            # 按日期过滤
            if 'start_date' in filters or 'end_date' in filters:
                if 'date' in df.columns:
                    date_col = self._parse_chinese_date(filtered_df['date'])
                    if 'start_date' in filters:
                        start_date = pd.to_datetime(filters['start_date'])
                        filtered_df = filtered_df[date_col >= start_date]
                    if 'end_date' in filters:
                        end_date = pd.to_datetime(filters['end_date'])
                        filtered_df = filtered_df[date_col <= end_date]

            # 按地区过滤
            if 'region' in filters and 'region' in df.columns:
                region_filter = filters['region']
                if isinstance(region_filter, str):
                    filtered_df = filtered_df[filtered_df['region'].str.contains(region_filter, na=False)]
                elif isinstance(region_filter, list):
                    filtered_df = filtered_df[filtered_df['region'].isin(region_filter)]

            # 按降雨量范围过滤
            if 'min_rainfall' in filters or 'max_rainfall' in filters:
                if 'rainfall' in df.columns:
                    rainfall_col = pd.to_numeric(filtered_df['rainfall'], errors='coerce')
                    if 'min_rainfall' in filters:
                        filtered_df = filtered_df[rainfall_col >= filters['min_rainfall']]
                    if 'max_rainfall' in filters:
                        filtered_df = filtered_df[rainfall_col <= filters['max_rainfall']]

        except Exception as e:
            self.logger.error(f"Error filtering data: {e}")
            return df

        return filtered_df

    def read_all_files(self) -> Dict[str, pd.DataFrame]:
        """Read all available data files and return as dict"""
        all_data = {}
        available_files = self.get_available_files()

        for filename in available_files:
            df = self.read_data_file(filename)
            if df is not None:
                all_data[filename] = df
                self.logger.info(f"Successfully loaded {filename}: {len(df)} records")
            else:
                self.logger.warning(f"Failed to load {filename}")

        return all_data

    def get_combined_data_summary(self) -> Dict[str, Any]:
        """Get summary of all available data files combined"""
        all_data = self.read_all_files()
        if not all_data:
            return {}

        total_records = 0
        all_regions = set()
        min_date = None
        max_date = None
        total_rainfall = 0
        all_rainfall_values = []
        file_summaries = {}

        for filename, df in all_data.items():
            file_records = len(df)
            total_records += file_records

            # 收集地区信息
            if 'region' in df.columns:
                all_regions.update(df['region'].dropna().unique())

            # 收集日期范围
            if 'date' in df.columns:
                date_col = self._parse_chinese_date(df['date']).dropna()
                if not date_col.empty:
                    file_min_date = date_col.min()
                    file_max_date = date_col.max()
                    if min_date is None or file_min_date < min_date:
                        min_date = file_min_date
                    if max_date is None or file_max_date > max_date:
                        max_date = file_max_date

            # 收集降雨量数据
            if 'rainfall' in df.columns:
                rainfall_col = pd.to_numeric(df['rainfall'], errors='coerce').dropna()
                if not rainfall_col.empty:
                    total_rainfall += rainfall_col.sum()
                    all_rainfall_values.extend(rainfall_col.tolist())

            # 记录每个文件的摘要
            file_summaries[filename] = {
                'records': file_records,
                'regions': list(df['region'].dropna().unique()) if 'region' in df.columns else [],
                'date_range': {
                    'start': date_col.min().strftime('%Y-%m-%d') if not date_col.empty else None,
                    'end': date_col.max().strftime('%Y-%m-%d') if not date_col.empty else None
                } if 'date' in df.columns and not date_col.empty else None,
                'rainfall_summary': {
                    'total': float(rainfall_col.sum()),
                    'mean': float(rainfall_col.mean()),
                    'max': float(rainfall_col.max()),
                    'min': float(rainfall_col.min())
                } if 'rainfall' in df.columns and not rainfall_col.empty else None
            }

        # 计算综合统计
        rainfall_stats = {}
        if all_rainfall_values:
            rainfall_series = pd.Series(all_rainfall_values)
            rainfall_stats = {
                'total': float(rainfall_series.sum()),
                'mean': float(rainfall_series.mean()),
                'median': float(rainfall_series.median()),
                'min': float(rainfall_series.min()),
                'max': float(rainfall_series.max()),
                'std': float(rainfall_series.std())
            }

        return {
            'total_files': len(all_data),
            'total_records': total_records,
            'all_regions': list(all_regions),
            'date_range': {
                'start': min_date.strftime('%Y-%m-%d') if min_date else None,
                'end': max_date.strftime('%Y-%m-%d') if max_date else None
            },
            'rainfall_stats': rainfall_stats,
            'file_summaries': file_summaries
        }

    def clear_cache(self):
        """Clear data cache"""
        self.cache.clear()
        self.logger.info("Data cache cleared")