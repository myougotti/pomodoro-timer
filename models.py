import os
import sqlite3
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pomodoro.db")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL,
                duration_seconds INTEGER NOT NULL,
                task_label TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def record_session(self, session_type, duration_seconds, task_label, started_at):
        self.conn.execute(
            """INSERT INTO sessions (session_type, duration_seconds, task_label, started_at, completed_at)
               VALUES (?, ?, ?, ?, ?)""",
            (session_type, duration_seconds, task_label,
             datetime.fromtimestamp(started_at).isoformat(),
             datetime.now().isoformat()),
        )
        self.conn.commit()

    def get_today_stats(self):
        today = datetime.now().strftime("%Y-%m-%d")
        row = self.conn.execute(
            """SELECT COUNT(*) as count, COALESCE(SUM(duration_seconds), 0) as total
               FROM sessions
               WHERE session_type = 'work' AND date(completed_at) = ?""",
            (today,),
        ).fetchone()
        return {"pomodoros": row["count"], "focus_seconds": row["total"]}

    def get_week_stats(self):
        rows = self.conn.execute(
            """SELECT date(completed_at) as day,
                      COUNT(*) as count,
                      SUM(duration_seconds) as total
               FROM sessions
               WHERE session_type = 'work'
                 AND date(completed_at) >= date('now', '-6 days')
               GROUP BY date(completed_at)
               ORDER BY day"""
        ).fetchall()
        return [{"day": r["day"], "pomodoros": r["count"], "focus_seconds": r["total"]} for r in rows]

    def get_all_time_stats(self):
        row = self.conn.execute(
            """SELECT COUNT(*) as count, COALESCE(SUM(duration_seconds), 0) as total
               FROM sessions WHERE session_type = 'work'"""
        ).fetchone()
        return {"pomodoros": row["count"], "focus_seconds": row["total"]}

    def close(self):
        self.conn.close()
