# ================================================================
#  db.py — PostgreSQL database access via psycopg2
# ================================================================
import datetime

try:
    import psycopg2
    import psycopg2.extras
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    _PSYCOPG2_AVAILABLE = False

# ── Edit these to match your local Postgres setup ──────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "dbname":   "snake_db",
    "user":     "postgres",
    "password": "postgres",
}
# ───────────────────────────────────────────────────────────────


def _connect():
    if not _PSYCOPG2_AVAILABLE:
        return None
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[DB] Connection failed: {e}")
        return None


def init_db():
    """Create tables if they don't exist. Returns True on success."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id       SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL
                    );
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS game_sessions (
                        id            SERIAL PRIMARY KEY,
                        player_id     INTEGER REFERENCES players(id),
                        score         INTEGER   NOT NULL,
                        level_reached INTEGER   NOT NULL,
                        played_at     TIMESTAMP DEFAULT NOW()
                    );
                """)
        return True
    except Exception as e:
        print(f"[DB] init_db failed: {e}")
        return False
    finally:
        conn.close()


def _get_or_create_player(cur, username: str) -> int:
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) RETURNING id",
        (username,)
    )
    return cur.fetchone()[0]


def save_result(username: str, score: int, level_reached: int) -> bool:
    """Insert a game session record. Returns True on success."""
    conn = _connect()
    if conn is None:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                pid = _get_or_create_player(cur, username)
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (pid, score, level_reached)
                )
        return True
    except Exception as e:
        print(f"[DB] save_result failed: {e}")
        return False
    finally:
        conn.close()


def get_leaderboard(limit: int = 10) -> list[dict]:
    """Return top-N all-time scores as list of dicts."""
    conn = _connect()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT p.username, gs.score, gs.level_reached,
                       gs.played_at::date AS played_date
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT %s
            """, (limit,))
            return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[DB] get_leaderboard failed: {e}")
        return []
    finally:
        conn.close()


def get_personal_best(username: str) -> int | None:
    """Return the player's best score, or None if no record."""
    conn = _connect()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT MAX(gs.score)
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                WHERE p.username = %s
            """, (username,))
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_personal_best failed: {e}")
        return None
    finally:
        conn.close()