"""
Modul Pengurusan Pangkalan Data (Database Layer)
Menyokong SQLite secara automatik untuk penyimpanan data.
"""

import os
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# Lokasi fail database SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "threads_data.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Bina jadual database sekiranya belum wujud."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threads_posts (
            post_id TEXT PRIMARY KEY,
            author_username TEXT NOT NULL,
            author_display_name TEXT,
            content_text TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            shares_count INTEGER DEFAULT 0,
            post_url TEXT NOT NULL,
            posted_at TIMESTAMP NOT NULL,
            viral_score REAL DEFAULT 0,
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def upsert_post(post: Dict[str, Any]):
    """
    Masukkan data post baharu atau kemas kini metrik jika sudah wujud.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO threads_posts (
            post_id, author_username, author_display_name, content_text,
            likes_count, comments_count, shares_count, post_url,
            posted_at, viral_score, crawled_at
        ) VALUES (
            :post_id, :author_username, :author_display_name, :content_text,
            :likes_count, :comments_count, :shares_count, :post_url,
            :posted_at, :viral_score, :crawled_at
        )
        ON CONFLICT(post_id) DO UPDATE SET
            likes_count = excluded.likes_count,
            comments_count = excluded.comments_count,
            shares_count = excluded.shares_count,
            viral_score = excluded.viral_score,
            crawled_at = excluded.crawled_at
    """, post)
    conn.commit()
    conn.close()

def get_top_posts(timeframe: str = "24h", min_likes: int = 500, min_comments: int = 500, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Tarik Top Posts berdasarkan:
    - timeframe: '24h' (24 jam) atau '7d' (seminggu)
    - min_likes >= 500
    - min_comments >= 500
    - Susunan markah viral tertinggi
    """
    now = datetime.now(timezone.utc)
    if timeframe == "24h":
        cutoff_time = (now - timedelta(hours=24)).isoformat()
    elif timeframe == "7d":
        cutoff_time = (now - timedelta(days=7)).isoformat()
    else:
        cutoff_time = (now - timedelta(days=30)).isoformat()

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM threads_posts
        WHERE posted_at >= ?
          AND likes_count >= ?
          AND comments_count >= ?
        ORDER BY viral_score DESC
        LIMIT ?
    """, (cutoff_time, min_likes, min_comments, limit))
    
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_stats() -> Dict[str, Any]:
    """Ringkasan statistik keseluruhan."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, MAX(likes_count) as max_likes, MAX(comments_count) as max_comments FROM threads_posts")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "max_likes": 0, "max_comments": 0}

# Inisialisasi DB secara automatik
init_db()
