from __future__ import annotations
import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv()

def run_sql_file(conn, path: Path):
    with path.open("r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()


def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL not set. Copy backend/.env.example to backend/.env and fill it.")
    here = Path(__file__).resolve().parents[1]
    schema = here / "db" / "schema.sql"
    seed = here / "db" / "seed.sql"
    with psycopg.connect(db_url) as conn:
        run_sql_file(conn, schema)
        run_sql_file(conn, seed)
    print("Database initialized and seeded.")

if __name__ == "__main__":
    main()
