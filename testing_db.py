from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:arnur@localhost:5432/tirek"

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print("Connection failed:", e)