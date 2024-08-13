import requests

def binance_contract_pairs():
    """
    Get all contract trading pairs from Binance.
    
    :return: A list of contract trading pairs
    """
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()
    
    usdt_pairs = [symbol['symbol'] for symbol in data['symbols'] if 'USDT' in symbol['symbol']]
    return usdt_pairs