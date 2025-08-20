import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HOST = "0.0.0.0"
PORT = 8000
SQL_REGENERATE_LIMIT = 2
SQL_EXECUTION_LIMIT = 2
