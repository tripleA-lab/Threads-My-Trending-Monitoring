"""
Penjana Laman Web GitHub Pages (index.html)
Memaparkan Top 10 Isu Paling Hangat & Viral di Threads (Komen > 500).
"""

from datetime import datetime
from db.database import get_top_posts, get_stats

def generate_dashboard():
    # Dapatkan Top 10 Isu Hangat
    top_posts = get_top_posts(min_comments=500, limit=10)
    stats = get_stats()
    updated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    cards = []
    for rank, p in enumerate(top_posts, 1):
        # Format nombor kemas
        comments_k = f"{p['comments_count']:,}"
        likes_k = f"{p['likes_count']:,}"
        shares_k = f"{p['shares_count']:,}"
        
        # Pangkat emas/perak untuk Top 3
        rank_badge_bg = "bg-amber-400 text-black font-black" if rank == 1 else ("bg-gray-200 text-black font-bold" if rank in [2, 3] else "bg-gray-700 text-white font-bold")

        card = f"""
        <div class="bg-gray-900/90 hover:bg-gray-800/90 border border-gray-800 hover:border-gray-700 rounded-2xl p-6 transition duration-200 shadow-lg">
            <div class="flex items-center justify-between mb-3">
                <div class="flex items-center space-x-3">
                    <span class="{rank_badge_bg} text-xs px-2.5 py-1 rounded-full">#{rank}</span>
                    <span class="font-bold text-white text-base tracking-wide">@{p['author_username']}</span>
                    <span class="text-xs text-gray-500 font-medium">• {p['author_display_name']}</span>
                </div>
                <span class="bg-rose-500/10 text-rose-400 text-xs font-semibold px-3 py-1 rounded-full border border-rose-500/20">
                    ⚡ Viral Score: {p['viral_score']:,.0f}
                </span>
            </div>
            
            <p class="text-gray-200 text-sm md:text-base leading-relaxed mb-5">
                {p['content_text']}
            </p>
            
            <div class="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-gray-800/80">
                <div class="flex items-center space-x-2">
                    <span class="bg-sky-500/10 text-sky-400 text-xs px-3 py-1.5 rounded-lg border border-sky-500/20 font-semibold">
                        💬 <b class="text-white">{comments_k}</b> Komen
                    </span>
                    <span class="bg-gray-800 text-gray-300 text-xs px-3 py-1.5 rounded-lg">
                        ❤️ <b class="text-white">{likes_k}</b> Likes
                    </span>
                    <span class="bg-gray-800 text-gray-300 text-xs px-3 py-1.5 rounded-lg">
                        🔄 <b class="text-white">{shares_k}</b> Shares
                    </span>
                </div>
                <a href="{p['post_url']}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-1.5 bg-white hover:bg-gray-200 text-black font-semibold text-xs px-4 py-2 rounded-xl transition shadow">
                    <span>Lihat Perbincangan di Threads</span>
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                </a>
            </div>
        </div>
        """
        cards.append(card)

    cards_html = "\n".join(cards)

    html_content = f"""<!DOCTYPE html>
<html lang="ms">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Threads Viral Monitor | Top 10 Isu Paling Hangat</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0b0e14; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
    </style>
</head>
<body class="text-gray-100 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-8">
        
        <!-- Header -->
        <header class="flex items-center justify-between pb-6 border-b border-gray-800">
            <div class="flex items-center space-x-3">
                <div class="w-11 h-11 bg-white text-black font-black flex items-center justify-center rounded-2xl text-2xl shadow">🧵</div>
                <div>
                    <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-white">Threads Viral Monitor</h1>
                    <p class="text-xs md:text-sm text-gray-400">Pemantauan Top 10 Isu Paling Hangat & Spike (Komen > 500)</p>
                </div>
            </div>
            <div class="text-right">
                <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    🟢 Sistem Aktif
                </span>
                <p class="text-[11px] text-gray-500 mt-1">Kemaskini: {updated_at}</p>
            </div>
        </header>

        <!-- Ringkasan Statistik -->
        <div class="grid grid-cols-3 gap-4 my-6">
            <div class="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
                <p class="text-xs text-gray-400 uppercase font-semibold">Total Post Disemak</p>
                <p class="text-xl md:text-2xl font-bold text-white mt-1">{stats['total']} Isu</p>
            </div>
            <div class="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
                <p class="text-xs text-gray-400 uppercase font-semibold">Komen Tertinggi</p>
                <p class="text-xl md:text-2xl font-bold text-sky-400 mt-1">{stats['max_comments']:,}</p>
            </div>
            <div class="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
                <p class="text-xs text-gray-400 uppercase font-semibold">Like Tertinggi</p>
                <p class="text-xl md:text-2xl font-bold text-rose-400 mt-1">{stats['max_likes']:,}</p>
            </div>
        </div>

        <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-white flex items-center space-x-2">
                <span>🔥 Senarai Top 10 Isu Paling Spike</span>
            </h2>
            <span class="text-xs text-gray-400">Disusun mengikut perbincangan paling hangat</span>
        </div>

        <!-- Senarai Top 10 -->
        <div class="space-y-4">
            {cards_html}
        </div>

        <!-- Footer -->
        <footer class="mt-14 pt-6 border-t border-gray-800/80 text-center text-xs text-gray-500">
            <p>Dibina untuk Automasi Cloud Portfolio • Data dipantau secara berkala dari Meta Threads</p>
        </footer>
    </div>
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Berjaya menjana index.html versi baharu!")

if __name__ == "__main__":
    generate_dashboard()
