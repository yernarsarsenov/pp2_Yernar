import psycopg2
from config import load_config
import os

def connect():
    """ Connect to the PostgreSQL database server """
    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return None

def run_sql_file(filename):
    """ Run a SQL file """
    conn = connect()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # Get the absolute path to the sql file
                file_path = os.path.join(os.path.dirname(__file__), filename)
                with open(file_path, 'r') as f:
                    cur.execute(f.read())
            conn.commit()
            print(f"Executed {filename} successfully.")
        except (psycopg2.DatabaseError, Exception) as error:
            print(f"Error executing {filename}: {error}")
        finally:
            conn.close()

if __name__ == '__main__':
    run_sql_file('schema.sql')
    run_sql_file('procedures.sql')
