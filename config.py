import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key_change_me')
    SQLITE_DB = os.environ.get('SQLITE_DB', 'college_ems.db')
