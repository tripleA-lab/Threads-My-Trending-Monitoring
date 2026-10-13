"""
Modul Algoritma Ranking & Pengiraan Skor Viral
Formula mengambil kira keutamaan Komen (perbincangan hangat), Shares, dan Likes.
"""

import re
from typing import Union

def parse_metric_count(val: Union[str, int, float]) -> int:
    """
    Tukar teks metrik seperti '1.2K', '50K', '1M' kepada nombor integer sebenar.
    """
    if isinstance(val, (int, float)):
        return int(val)
    
    val_str = str(val).strip().upper().replace(",", "")
    if not val_str:
        return 0
    
    match = re.match(r"^([\d\.]+)\s*([KMB])?$", val_str)
    if not match:
        digits = re.findall(r"\d+", val_str)
        return int(digits[0]) if digits else 0
    
    number_part, unit = match.groups()
    try:
        number = float(number_part)
        if unit == "K":
            return int(number * 1000)
        elif unit == "M":
            return int(number * 1000000)
        elif unit == "B":
            return int(number * 1000000000)
        return int(number)
    except ValueError:
        return 0

def calculate_viral_score(likes: int, comments: int, shares: int = 0) -> float:
    """
    Formula Pengiraan Skor Viral:
    - Likes: Berat 1x
    - Shares / Reposts: Berat 2x
    - Comments: Berat 3x (tanda isu trending & perbincangan hangat)
    """
    score = (likes * 1.0) + (shares * 2.0) + (comments * 3.0)
    return round(score, 2)

def is_viral_candidate(likes: int, comments: int, min_likes: int = 500, min_comments: int = 500) -> bool:
    """
    Syarat kelayakan minimum: Like > 500 dan Komen > 500.
    """
    return likes >= min_likes and comments >= min_comments
