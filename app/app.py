"""
Dashboard Monitoring Threads Trending & Viral
Frontpage UI dibina dengan Streamlit untuk Portfolio Web & Data Engineering.
"""

import os
import sys
import streamlit as st

# Tambah path utama
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import get_top_posts, get_stats
from scraper.threads_scraper import seed_sample_viral_data

st.set_page_config(
    page_title="Threads Viral Monitor | Top 10 Trending",
    page_icon="🧵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (CSS) untuk paparan kad moden Threads
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .post-card {
        border: 1px solid rgba(125, 125, 125, 0.2);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 16px;
        background-color: rgba(125, 125, 125, 0.04);
        transition: transform 0.15s ease-in-out;
    }
    .post-card:hover {
        transform: translateY(-2px);
        border-color: #000;
    }
    .badge-rank {
        background-color: #111;
        color: #fff;
        font-weight: bold;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
        margin-right: 8px;
    }
    .badge-viral {
        background-color: #ffefe6;
        color: #e04400;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.82rem;
        display: inline-block;
    }
    .badge-stat {
        background-color: rgba(125, 125, 125, 0.12);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        margin-right: 10px;
    }
    .post-author {
        font-weight: 700;
        font-size: 1.05rem;
    }
    .post-content {
        margin-top: 10px;
        margin-bottom: 14px;
        font-size: 1.02rem;
        line-height: 1.5;
    }
    .threads-btn {
        background-color: #000000;
        color: #ffffff !important;
        text-decoration: none;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 5px;
    }
    .threads-btn:hover {
        background-color: #333333;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# Menu Bar Tepi (Sidebar)
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9d/Threads_%28app%29_logo.svg", width=55)
    st.title("🧵 Tetapan Monitor")
    st.markdown("Dashboard pemantauan topik paling hangat di **Meta Threads**.")
    
    st.divider()
    st.subheader("🎯 Kriteria Tapisan")
    min_likes = st.number_input("Minimum Likes", value=500, step=100)
    min_comments = st.number_input("Minimum Komen", value=500, step=100)
    
    st.markdown("""
    **Formula Skor Viral:**  
    `Skor = (Like × 1) + (Share × 2) + (Komen × 3)`
    """)
    
    st.divider()
    st.subheader("🛠️ Pengurusan Data")
    if st.button("🔄 Suntik / Muat Semula Data Contoh"):
        seed_sample_viral_data()
        st.success("Data berjaya dimuat semula!")
        st.rerun()

    st.caption("Dibina untuk Projek Portfolio Automasi Cloud.")

# Bahagian Utama (Header & Metrik)
st.markdown('<div class="main-header">🧵 Threads Viral & Trending Monitor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Pemantauan Top 10 Isu & Perbincangan Terhangat (Komen > 500, Like > 500)</div>', unsafe_allow_html=True)

stats = get_stats()
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Post Dipantau", f"{stats['total']} Post")
with col2:
    st.metric("Like Tertinggi", f"{stats['max_likes']:,}" if stats['max_likes'] else "0")
with col3:
    st.metric("Komen Tertinggi", f"{stats['max_comments']:,}" if stats['max_comments'] else "0")
with col4:
    st.metric("Status Automasi", "🟢 Aktif (Cloud Cron)")

st.write("")

# Tab Masa: 24 Jam & 7 Hari
tab_24h, tab_7d = st.tabs(["🔥 24 Jam Terkini (Hari Ini)", "📅 7 Hari Terkini (Seminggu)"])

def render_post_list(posts, title):
    if not posts:
        st.info(f"Tiada post yang melepasi kriteria (Likes ≥ {min_likes}, Komen ≥ {min_comments}) dalam tempoh ini. Sila klik 'Suntik Data Contoh' di menu tepi.")
        return

    st.write(f"Menunjukkan **Top {len(posts)}** post viral mengikut skor interaksi:")
    
    for rank, p in enumerate(posts, 1):
        posted_dt = p['posted_at'][:16].replace("T", " ")
        
        st.markdown(f"""
        <div class="post-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="badge-rank">#{rank}</span>
                    <span class="post-author">@{p['author_username']}</span>
                    <span style="color: #888; font-size: 0.85rem; margin-left: 8px;">• {posted_dt} UTC</span>
                </div>
                <div>
                    <span class="badge-viral">⚡ Viral Score: {p['viral_score']:,.0f}</span>
                </div>
            </div>
            <div class="post-content">
                {p['content_text']}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span class="badge-stat">💬 <b>{p['comments_count']:,}</b> Komen</span>
                    <span class="badge-stat">❤️ <b>{p['likes_count']:,}</b> Likes</span>
                    <span class="badge-stat">🔄 <b>{p['shares_count']:,}</b> Shares</span>
                </div>
                <div>
                    <a href="{p['post_url']}" target="_blank" class="threads-btn">
                        👉 Buka Post di Threads ↗
                    </a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_24h:
    posts_24h = get_top_posts(timeframe="24h", min_likes=min_likes, min_comments=min_comments, limit=10)
    render_post_list(posts_24h, "24 Jam")

with tab_7d:
    posts_7d = get_top_posts(timeframe="7d", min_likes=min_likes, min_comments=min_comments, limit=10)
    render_post_list(posts_7d, "Seminggu")
