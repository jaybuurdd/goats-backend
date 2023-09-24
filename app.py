from typing import Union
from fastapi import FastAPI
from utils.database import config_db
from utils.logging import config_logging
from config import get_config

CONFIG = get_config()
api = FastAPI()
config_logging(CONFIG)
db = config_db(CONFIG)

