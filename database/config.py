import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KEY = os.environ.get("KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")