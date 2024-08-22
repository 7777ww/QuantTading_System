
import os
import json
from mongoengine import register_connection
from model import OHLCV
from .get_data import get_ohlcv_data_as_df




PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')
DATABASE_CONFIG_FILE = os.path.join(CONFIG_DIR, 'database.json')

def load_config(DATABASE_CONFIG_FILE=DATABASE_CONFIG_FILE):
    with open(DATABASE_CONFIG_FILE, 'r') as file:
        config = json.load(file)
    return config

config = load_config(DATABASE_CONFIG_FILE)

def init_db():
    """Initialize the database connection."""
    config = load_config()
    uri = config['mongodb']['uri']
    db_name = config['mongodb']['name']
    
    # Register the MongoDB connection
    register_connection(
        alias='default',
        host=uri,
        db=db_name
    )

# Initialize the database when the package is imported
init_db()



