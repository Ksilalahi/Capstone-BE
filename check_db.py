from db_config import engine
from sqlalchemy import text

with engine.connect() as conn:
    print(conn.execute(text("SELECT COUNT(*) FROM users")).fetchone())
    print(conn.execute(text("SELECT COUNT(*) FROM transactions")).fetchone())
    print(conn.execute(text("SELECT COUNT(*) FROM interactions")).fetchone())