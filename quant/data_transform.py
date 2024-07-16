
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
from dateutil import parser
def convert_columns_to_string(data: pd.DataFrame, columns: list, date_format: str = '%Y-%m-%d %H:%M:%S') -> pd.DataFrame:
    """
    将 DataFrame 中指定的时间戳列转换为字符串格式。

    :param data: 包含时间戳列的 pandas DataFrame
    :param columns: 要转换的列名列表
    :param date_format: 目标日期字符串格式，默认为 '%Y-%m-%d %H:%M:%S'
    :return: 转换后的 pandas DataFrame
    """
    for column in columns:
        if column in data.columns:
            data[column] = pd.to_datetime(data[column], unit='ms')
            data[column] = data[column].dt.strftime(date_format)
    return data
    
def rename_and_reorder_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    重命名并调整 DataFrame 中的列顺序。

    :param data: 包含查询数据的 pandas DataFrame
    :return: 调整后的 pandas DataFrame
    """

    if '_id' in data.columns:
        data.drop(columns=['_id'], inplace=True)
    if 'timestamp' in data.columns:
        data.rename(columns={'timestamp': 'open_time'}, inplace=True)
    columns_order = ['open_time', 'close_time'] + [col for col in data.columns if col not in ['open_time', 'close_time']]
    data = data[columns_order]

    return data
def convert_to_timestamp(date_string):
    """
    根据输入的日期字符串自动调整日期格式并将其转换为 Unix 时间戳。

    :param date_string: 要转换的日期字符串
    :return: Unix 时间戳
    """
    dt = parser.parse(date_string)
    return int(dt.timestamp()*1000)