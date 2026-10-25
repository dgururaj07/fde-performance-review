import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. Create a .env file with DATABASE_URL=postgresql://user:password@host:port/database"
    )

print('connection string:', DATABASE_URL)


def get_connection():
    """Establishes a connection to the PostgreSQL database using the DATABASE_URL from environment variables."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set. Please configure your .env file.")

    try:
        conn = psycopg.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise RuntimeError(f"Error connecting to the database: {e}") from e 