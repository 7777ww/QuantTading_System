# # QunatTraing_System/mongodb/models/__init__.py
from mongodb.model.ohlcv import OHLCV
# import os
# import importlib
# from mongoengine import Document

# # get all file
# current_dir = os.path.dirname(__file__)
# model_files = [f[:-3] for f in os.listdir(current_dir) if f.endswith('.py') and f != '__init__.py']

# #import all model
# for model_name in model_files:
#     importlib.import_module(f'.{model_name}', package='mongodb.model')

# __all__ = [name for name, cls in globals().items() if isinstance(cls, type) and issubclass(cls, Document)]
