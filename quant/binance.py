import requests

def get_binance_contract_pairs():
    """
    Get all contract trading pairs from Binance.
    
    :return: A list of contract trading pairs
    """
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()
    
    usdt_pairs = [symbol['symbol'] for symbol in data['symbols'] if 'USDT' in symbol['symbol']]
    return usdt_pairs

from pymongo import UpdateOne, MongoClient


def bulk_upsert(collection, data_dict):
    """
    Perform a bulk upsert operation on a MongoDB collection.

    :param collection: The MongoDB collection to perform the operation on.
    :param data_dict: A list of dictionaries, each representing a document to be upserted.
    :return: A summary of the bulk upsert operation.
    """
    operations = []
    for doc in data_dict:
        operations.append(
            UpdateOne(
                {"timestamp": doc["timestamp"]},  # Matching condition, use another unique field if necessary
                {"$set": doc},  # Update content
                upsert=True  # Insert if it doesn't exist
            )
        )

    try:
        result = collection.bulk_write(operations)
        return f"Inserted or updated {result.upserted_count + result.modified_count} documents"
    except Exception as e:
        return f"Operation failed: {e}"