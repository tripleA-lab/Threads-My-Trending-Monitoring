"""
Penjana Laman Web GitHub Pages (index.html)
Membaca data Top 10 dari database dan menghasilkan antaramuka moden berasaskan Tailwind CSS.
"""

import os
import json
from datetime import datetime
from db.database import get_top_posts, get_stats

def generate_dashboard():
    # Tarik data Top 10 untuk 24 Jam dan 7 Hari
    posts_24h = get_top_posts(timeframe="24h", min_likes=500, min_comments=500, limit=10)
    posts_7d = get_top_posts(timeframe="7d", min_likes=500, min_comments=500, limit=10)
    stats = get_stats()
    
    updated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def build_cards_html(posts):
        if not posts:
            return """
            <div class="bg-gray-800/40 rounded-xl p-8 text-center border border-gray-700/50">
                <p class="text-gray-400">Tiada post melepasi kriteria (Likes ≥ 500 & Komen ≥ 500) pada masa ini.</p>
            </div>
            """
        
        cards = []
        for rank, p in enumerate(posts, 1):
            posted_date = p['posted_at'][:16].replace("T", " ")
            card = f"""
            <div class="bg-gray-800/60 hover:bg-gray-800 border border-gray-700/60 hover:border-gray-600 rounded-2xl p-6 transition duration-200">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-3">
                        <span class="bg-white text-black font-extrabold text-xs px-2.5 py-1 rounded-full">#{rank}</span>
                        <span class="font-bold text-white text-base">@{p['author_username']}</span>
                        <span class="text-xs text-gray-400">• {posted_date} UTC</span>
                    </div>
                    <span class="bg-amber-500/10 text-amber-400 text-xs font-semibold px-3 py-1 rounded-full border border-amber-500/20">
                        ⚡ Viral Score: {p['viral_score']:,.0f}
                    </span>
                </div>
                
                <p class="text-gray-200 text-sm md:text-base leading-relaxed mb-4">
                    {p['content_text']}
                </p>
                
                <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-700/40">
                    <div class="flex items-center space-x-2">
                        <span class="bg-gray-700/50 text-gray-300 text-xs px-2.5 py-1 rounded-lg">💬 <b class="text-white">{p['comments_count']:,}</b> Komen</span>
                        <span class="bg-gray-700/50 text-gray-300 text-xs px-2.5 py-1 rounded-lg">❤️ <b class="text-white">{p['likes_count']:,}</b> Likes</span>
                        <span class="bg-gray-700/50 text-gray-300 text-xs px-2.5 py-1 rounded-lg">🔄 <b class="text-white">{p['shares_count']:,}</b> Shares</span>
                    </div>
                    <a href="{p['post_url']}" target="_blank" class="inline-flex items-center space-x-1.5 bg-white hover:bg-gray-200 text-black font-semibold text-xs px-3.5 py-1.5 rounded-lg transition">
                        <span>Buka di Threads</span>
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                    </a>
                </div>
            </div>
            """
            cards.append(card)
        return "\n".join(cards)

    html_content = f"""<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Threads Viral Monitor | Top 10 Trending</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0d1117; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
        .tab-btn.active {{ border-bottom: 2px solid #ffffff; color: #ffffff; font-weight: 700; }}
    </style>
</head>
<body class="text-gray-100 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-8">
        
        <!-- Header -->
        <header class="flex items-center justify-between pb-6 border-b border-gray-800">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-white text-black font-black flex items-center justify-center rounded-xl text-xl">🧵</div>
                <div>
                    <h1 class="text-2xl font-bold tracking-tight text-white">Threads Viral Monitor</h1>
                    <p class="text-xs text-gray-400">Pantauan Isu Terhangat (Komen > 500, Likes > 500)</p>
                </div>
            </div>
            <div class="text-right">
                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    🟢 Automasi Aktif
                </span>
                <p class="text-[11px] text-gray-500 mt-1">Kemaskini: {updated_at}</p>
            </div>
        </header>

        <!-- Ringkasan Metrik -->
        <div class="grid grid-cols-3 gap-4 my-6">
            <div class="bg-gray-800/40 border border-gray-700/50 rounded-xl p-4">
                <p class="text-xs text-gray-400 uppercase font-semibold">Total Post</p>
                <p class="text-xl font-bold text-white mt-1">{stats['total']} Post</p>
            </div>
            <div class="bg-gray-800/40 border border-gray-700/50 rounded-xl p-4">
                <p class="text-xs text-gray-400 uppercase font-semibold">Like Tertinggi</p>
                <p class="text-xl font-bold text-rose-400 mt-1">{stats['max_likes']:,}</p>
            </div>
            <div class="bg-gray-800/40 border border-gray-700/50 rounded-xl p-4">
                <p class="text-xs text-gray-400 uppercase font-semibold">Komen Tertinggi</p>
                <p class="text-xl font-bold text-sky-400 mt-1">{stats['max_comments']:,}</p>
            </div>
        </div>

        <!-- Tab Navigasi (24 Jam vs Seminggu) -->
        <div class="flex space-x-6 border-b border-gray-800 mb-6 text-sm text-gray-400">
            <button onclick="switchTab('tab-24h')" id="btn-24h" class="tab-btn active pb-3 transition">
                🔥 24 Jam Terkini (Hari Ini)
            </button>
            <button onclick="switchTab('tab-7d')" id="btn-7d" class="tab-btn pb-3 transition">
                📅 7 Hari Terkini (Seminggu)
            </button>
        </div>

        <!-- Kandungan Tab 24 Jam -->
        <div id="tab-24h" class="space-y-4">
            {build_cards_html(posts_24h)}
        </div>

        <!-- Kandungan Tab 7 Hari -->
        <div id="tab-7d" class="space-y-4 hidden">
            {build_cards_html(posts_7d)}
        </div>

        <!-- Footer -->
        <footer class="mt-12 pt-6 border-t border-gray-800 text-center text-xs text-gray-500">
            <p>Dibina untuk Automasi Cloud Portfolio • Data dipantau secara berkala dari Meta Threads</p>
        </footer>
    </div>

    <script>
        function switchTab(tabId) {{
            document.getElementById('tab-24h').classList.add('hidden');
            document.getElementById('tab-7d').classList.add('hidden');
            document.getElementById('btn-24h').classList.remove('active');
            document.getElementById('btn-7d').classList.remove('active');

            document.getElementById(tabId).classList.remove('hidden');
            if (tabId === 'tab-24h') {{
                document.getElementById('btn-24h').classList.add('active');
            }} else {{
                document.getElementById('btn-7d').classList.add('active');
            }}
        }}
    </script>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Berjaya menjana index.html untuk GitHub Pages!")

if __name__ == "__main__":
    generate_dashboard()
