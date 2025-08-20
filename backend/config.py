import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
SQL_REGENERATE_LIMIT = int(os.getenv("SQL_REGENERATE_LIMIT"))
SQL_EXECUTION_LIMIT = int(os.getenv("SQL_EXECUTION_LIMIT"))
