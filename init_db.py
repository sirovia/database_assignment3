"""Initialize database from SQL file."""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError


def normalize_database_url(database_url: str) -> str:
    """Normalize database URL for SQLAlchemy."""
    database_url = database_url.strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if "sslmode=" not in database_url:
        database_url += ("&" if "?" in database_url else "?") + "sslmode=require"
    return database_url


def init_database():
    """Initialize database from assigm3.sql file."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("No DATABASE_URL found, skipping initialization")
        return
    
    database_url = normalize_database_url(database_url)
    engine = create_engine(database_url)
    
    # Read SQL file
    sql_file = "assigm3.sql"
    if not os.path.exists(sql_file):
        print(f"SQL file {sql_file} not found, skipping initialization")
        return
    
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    # Split by semicolons and execute each statement
    statements = [s.strip() for s in sql_content.split(";") if s.strip() and not s.strip().startswith("--")]
    
    try:
        with engine.begin() as conn:
            # Check if tables already exist
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            if result.scalar():
                print("Database already initialized, skipping...")
                return
            
            print("Initializing database from SQL file...")
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        # Ignore errors for CREATE TABLE IF NOT EXISTS, etc.
                        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                            print(f"Warning: {e}")
            print("Database initialized successfully!")
    except OperationalError as e:
        print(f"Database connection error: {e}")
    except Exception as e:
        print(f"Error initializing database: {e}")


if __name__ == "__main__":
    init_database()

