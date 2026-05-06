from sqlalchemy import create_engine

DB_USER = "root"
DB_PASSWORD = "923456"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "bank"

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)