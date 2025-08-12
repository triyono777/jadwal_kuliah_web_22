from __future__ import annotations
"""
This helper is no longer needed when using Supabase hosted Postgres.
Use the SQL editor in the Supabase dashboard to run the contents of
`backend/db/schema.sql` and `backend/db/seed.sql`.
"""
from pathlib import Path

def print_instructions():
    here = Path(__file__).resolve().parents[1]
    schema = here / "db" / "schema.sql"
    seed = here / "db" / "seed.sql"
    print("Run these files in Supabase SQL editor:")
    print(f" - {schema}")
    print(f" - {seed}")

if __name__ == "__main__":
    print_instructions()
