"""
Modul Threads Scraper (Stealth & Human-Like Behavior)
1. Masa larian bawah 1 minit (< 45-50 saat).
2. Pergerakan santai ala manusia (Random delay antara skrol).
3. Penyamaran (Stealth User-Agent Chrome).
4. Penapisan automatik: Like > 500 & Komen > 500.
"""

import sys
import os
import time
import random
import logging
from datetime import datetime, timezone, timedelta

# Tambah root folder ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.database import upsert_post
from scraper.ranking import parse_metric_count, calculate_viral_score, is_viral_candidate

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"
]

def run_stealth_crawler(target_url: str = "https://www.threads.net", max_duration_sec: int = 45):
    """Jalankan crawler secara stealth dan perlahan dengan had masa bawah 1 minit."""
    logging.info(f"Memulakan Threads Stealth Crawler (Had masa: {max_duration_sec}s)...")
    start_time = time.time()
    extracted_count = 0
    saved_viral_count = 0

    try:
        from playwright.sync_api import sync_playwright
        try:
            from playwright_stealth import stealth_sync
            has_stealth = True
        except ImportError:
            has_stealth = False

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars"
                ]
            )
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                locale="ms-MY,en-US,en"
            )
            page = context.new_page()
            if has_stealth:
                stealth_sync(page)

            logging.info(f"Membuka laman: {target_url}")
            page.goto(target_url, timeout=30000, wait_until="domcontentloaded")
            
            # Delay awal pergerakan manusia
            time.sleep(random.uniform(2.0, 3.5))

            scroll_count = 0
            while (time.time() - start_time) < max_duration_sec:
                scroll_count += 1
                logging.info(f"Skrol santai ke-{scroll_count}...")
                
                # Skrol santai (human scrolling)
                scroll_distance = random.randint(400, 750)
                page.mouse.wheel(0, scroll_distance)
                
                # Delay santai 2 - 4 saat
                time.sleep(random.uniform(2.0, 4.0))

                # Cari post dalam halaman
                articles = page.query_selector_all("div[data-pressable-container='true'], article")
                for art in articles:
                    try:
                        link_el = art.query_selector("a[href*='/post/']")
                        if not link_el:
                            continue
                        href = link_el.get_attribute("href") or ""
                        if not href.startswith("http"):
                            href = f"https://www.threads.net{href}"
                        
                        post_id = href.rstrip("/").split("/")[-1]
                        user_el = art.query_selector("a[href^='/@']")
                        username = user_el.inner_text().strip().replace("@", "") if user_el else "threads_user"
                        
                        text_el = art.query_selector("span[dir='auto']")
                        content_text = text_el.inner_text().strip() if text_el else ""

                        buttons = art.query_selector_all("div[role='button'], button")
                        likes = 0
                        comments = 0
                        shares = 0
                        
                        for btn in buttons:
                            aria_label = btn.get_attribute("aria-label") or ""
                            txt = btn.inner_text().strip()
                            if "like" in aria_label.lower():
                                likes = parse_metric_count(txt or aria_label)
                            elif "reply" in aria_label.lower() or "comment" in aria_label.lower():
                                comments = parse_metric_count(txt or aria_label)
                            elif "repost" in aria_label.lower() or "share" in aria_label.lower():
                                shares = parse_metric_count(txt or aria_label)

                        extracted_count += 1
                        
                        # Tapis syarat: Like > 500 dan Komen > 500
                        if is_viral_candidate(likes, comments, min_likes=500, min_comments=500):
                            viral_score = calculate_viral_score(likes, comments, shares)
                            post_data = {
                                "post_id": post_id,
                                "author_username": username,
                                "author_display_name": username,
                                "content_text": content_text[:500],
                                "likes_count": likes,
                                "comments_count": comments,
                                "shares_count": shares,
                                "post_url": href,
                                "posted_at": datetime.now(timezone.utc).isoformat(),
                                "viral_score": viral_score,
                                "crawled_at": datetime.now(timezone.utc).isoformat()
                            }
                            upsert_post(post_data)
                            saved_viral_count += 1
                            logging.info(f"🔥 Jumpa Post Viral! [@{username}] Like: {likes}, Komen: {comments}")

                    except Exception:
                        continue

            browser.close()
            logging.info(f"Crawl selesai dalam {round(time.time() - start_time, 1)}s. Total diimbas: {extracted_count}, Viral disimpan: {saved_viral_count}")

    except Exception as e:
        logging.error(f"Ralat semasa crawler: {e}")

def seed_sample_viral_data():
    """Suntik sampel data Threads viral sebenar untuk paparan segera."""
    now = datetime.now(timezone.utc)
    sample_posts = [
        {
            "post_id": "post_viral_01",
            "author_username": "tech_malaysia",
            "author_display_name": "Tech Insight MY",
            "content_text": "Gaji fresh grad bidang IT & AI sekarang: Adakah pasaran kerja Malaysia makin kompetitif atau masih banyak kekosongan jawatan? Ramai luahkan pengalaman.",
            "likes_count": 3420,
            "comments_count": 1820,
            "shares_count": 640,
            "post_url": "https://www.threads.net/@zuck/post/C4v_sample1",
            "posted_at": (now - timedelta(hours=3)).isoformat(),
            "viral_score": calculate_viral_score(3420, 1820, 640),
            "crawled_at": now.isoformat()
        },
        {
            "post_id": "post_viral_02",
            "author_username": "kewangan_bijak",
            "author_display_name": "Kewangan Santai",
            "content_text": "Beli rumah pertama pada usia 25 tahun: Adakah langkah bijak atau beban komitmen bulanan? Ini analisis kos tersembunyi yang ramai terlepas pandang.",
            "likes_count": 5210,
            "comments_count": 2150,
            "shares_count": 910,
            "post_url": "https://www.threads.net/@mosseri/post/C4v_sample2",
            "posted_at": (now - timedelta(hours=8)).isoformat(),
            "viral_score": calculate_viral_score(5210, 2150, 910),
            "crawled_at": now.isoformat()
        },
        {
            "post_id": "post_viral_03",
            "author_username": "kerjaya_kita",
            "author_display_name": "Tip Temuduga",
            "content_text": "Hentikan meletakkan nombor IC dan alamat rumah lengkap dalam resume anda. Lindungi privasi diri daripada kebocoran maklumat syarikat palsu.",
            "likes_count": 8900,
            "comments_count": 940,
            "shares_count": 1420,
            "post_url": "https://www.threads.net/@threads/post/C4v_sample3",
            "posted_at": (now - timedelta(hours=14)).isoformat(),
            "viral_score": calculate_viral_score(8900, 940, 1420),
            "crawled_at": now.isoformat()
        },
        {
            "post_id": "post_viral_04",
            "author_username": "foodie_malaysia",
            "author_display_name": "Foodie KL",
            "content_text": "Kedai viral yang beratur panjang lebih sejam: Adakah makanannya benar-benar sedap atau sekadar hype media sosial? Ramai netizen beri ulasan jujur.",
            "likes_count": 4120,
            "comments_count": 1540,
            "shares_count": 520,
            "post_url": "https://www.threads.net/@creators/post/C4v_sample4",
            "posted_at": (now - timedelta(hours=20)).isoformat(),
            "viral_score": calculate_viral_score(4120, 1540, 520),
            "crawled_at": now.isoformat()
        },
        {
            "post_id": "post_viral_05",
            "author_username": "kesihatan_mental",
            "author_display_name": "Mindset Sihat",
            "content_text": "Tidur kurang 6 jam sehari secara berterusan memberi kesan negatif sama seperti mabuk alkohol ringan. Utamakan waktu rehat anda berbanding kerja lebih masa.",
            "likes_count": 11200,
            "comments_count": 1320,
            "shares_count": 2400,
            "post_url": "https://www.threads.net/@instagram/post/C4v_sample5",
            "posted_at": (now - timedelta(days=2)).isoformat(),
            "viral_score": calculate_viral_score(11200, 1320, 2400),
            "crawled_at": now.isoformat()
        },
        {
            "post_id": "post_viral_06",
            "author_username": "automotif_harian",
            "author_display_name": "Dunia Kereta",
            "content_text": "Kereta elektrik (EV) vs Kereta Petrol untuk pemanduan harian di Malaysia: Mana satu yang betul-betul menjimatkan kos penyelenggaraan selepas 3 tahun?",
            "likes_count": 6400,
            "comments_count": 1670,
            "shares_count": 830,
            "post_url": "https://www.threads.net/@design/post/C4v_sample6",
            "posted_at": (now - timedelta(days=4)).isoformat(),
            "viral_score": calculate_viral_score(6400, 1670, 830),
            "crawled_at": now.isoformat()
        }
    ]

    for p in sample_posts:
        upsert_post(p)
    logging.info(f"Berjaya menyuntik {len(sample_posts)} sampel data viral ke database!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="Suntik data contoh")
    parser.add_argument("--duration", type=int, default=45, help="Maksimum saat (<60s)")
    args = parser.parse_args()

    if args.seed:
        seed_sample_viral_data()
    else:
        run_stealth_crawler(max_duration_sec=args.duration)
