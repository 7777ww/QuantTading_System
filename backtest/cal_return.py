import numpy as np
import pandas as pd

def calculate_returns(training, positions, fraction):
    """
    計算報酬，考慮交易成本。

    參數:
    training (pd.DataFrame): 資產的價格數據。
    positions (pd.DataFrame): 每日資產的持倉。
    fraction (float): 每次持倉變動的交易成本比例。

    返回:
    pd.DataFrame: 包含計算後的報酬的 DataFrame。
    """
    # 1. Calculate daily returns
    
    training_ret = training.pct_change().dropna()
    
    # 2. Shift positions by one day to avoid look-ahead bias
    shifted_positions = positions.shift(1)
    
    # 3. Calculate daily returns contributed by each position
    ret = training_ret * shifted_positions
    
    # 4. Calculate transaction costs
    transaction_costs = fraction * np.abs(positions - shifted_positions)
    
    # 5. Subtract transaction costs from returns
    ret -= transaction_costs
    
    # 6. Remove NaN values
    ret.dropna(inplace=True)
    
    # 7. Sum returns across all assets to get total portfolio return for each day 
    ret['returns'] = ret.sum(axis=1)
    
    return ret 