import psycopg2
from configparser import ConfigParser
import os

def load_config(filename='database.ini', section='postgresql'):
    # In TSIS4, we'll look for database.ini in the same directory
    path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(path):
        # Fallback to a default if not found, but we will create it
        return {
            "host": "localhost",
            "database": "pp2",
            "user": "postgres",
            "password": "2008yernar",
            "port": "5432"
        }
    
    parser = ConfigParser()
    parser.read(path)
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    return config

class DBManager:
    def __init__(self):
        self.config = load_config()
        self.init_db()

    def get_connection(self):
        return psycopg2.connect(**self.config)

    def init_db(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS players (
                id       SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS game_sessions (
                id            SERIAL PRIMARY KEY,
                player_id     INTEGER REFERENCES players(id),
                score         INTEGER   NOT NULL,
                level_reached INTEGER   NOT NULL,
                played_at     TIMESTAMP DEFAULT NOW()
            )
            """
        )
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    for command in commands:
                        cur.execute(command)
                conn.commit()
        except Exception as e:
            print(f"Database init error: {e}")

    def get_user_id(self, username):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
                    row = cur.fetchone()
                    if row:
                        return row[0]
                    else:
                        cur.execute("INSERT INTO players (username) VALUES (%s) RETURNING id", (username,))
                        id = cur.fetchone()[0]
                        conn.commit()
                        return id
        except Exception as e:
            print(f"get_user_id error: {e}")
            return None

    def save_score(self, username, score, level):
        user_id = self.get_user_id(username)
        if user_id is None: return
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                        (user_id, score, level)
                    )
                conn.commit()
        except Exception as e:
            print(f"save_score error: {e}")

    def get_leaderboard(self):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.username, s.score, s.level_reached, s.played_at 
                        FROM game_sessions s
                        JOIN players p ON s.player_id = p.id
                        ORDER BY s.score DESC, s.level_reached DESC
                        LIMIT 10
                    """)
                    return cur.fetchall()
        except Exception as e:
            print(f"get_leaderboard error: {e}")
            return []

    def get_personal_best(self, username):
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT MAX(s.score) 
                        FROM game_sessions s
                        JOIN players p ON s.player_id = p.id
                        WHERE p.username = %s
                    """, (username,))
                    row = cur.fetchone()
                    return row[0] if row and row[0] is not None else 0
        except Exception as e:
            print(f"get_personal_best error: {e}")
            return 0
