from databases import Database
from sqlalchemy import create_engine
from config import settings

database = Database(settings.DATABASE_URL)
engine = create_engine(str(settings.DATABASE_URL).replace("asyncpg", "psycopg2"), pool_pre_ping=True)

