from db_config import engine

try:
    conn = engine.connect()
    print("Connected!")
    conn.close()
except Exception as e:
    print("ERROR DETAIL:")
    print(e)