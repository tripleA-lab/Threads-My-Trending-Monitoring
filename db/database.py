"""
Modul Pengurusan Pangkalan Data (Database Layer)
Fokus kepada Post yang Spike & Viral (Komen > 500) tanpa kekangan masa sempit.
"""

import os
import sqlite3
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "threads_data.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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

def get_top_posts(min_comments: int = 500, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Tarik Top 10 Isu Paling Spike & Hangat.
    Keutamaan kepada perbincangan rancak (Komen > 500) dan Viral Score.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM threads_posts
        WHERE comments_count >= ?
        ORDER BY viral_score DESC, comments_count DESC
        LIMIT ?
    """, (min_comments, limit))
    
    rows = cursor.fetchall()
    
    # Jika dalam DB kurang dari 10 post yang cecah 500 komen,
    # ambil baki post tertinggi supaya ranking sentiasa genap 10.
    if len(rows) < limit:
        cursor.execute("""
            SELECT * FROM threads_posts
            ORDER BY viral_score DESC, comments_count DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, MAX(likes_count) as max_likes, MAX(comments_count) as max_comments FROM threads_posts")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {"total": 0, "max_likes": 0, "max_comments": 0}

init_db()
