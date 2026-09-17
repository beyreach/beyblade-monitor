"""
ベイブレード関連商品限定 Amazon在庫復活チェック(通知専用・X投稿なし)

判定条件:
  1. カートボタンが存在し、かつ在庫切れ表記がない(在庫あり)
  2. 出品者が Amazon.co.jp 自身、または Prime バッジがある(Prime発送)

判定結果を state.json に書き込むだけ。通知は watcher.html 側(ブラウザ)が担当する。
"""

import json
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ASIN_FILE = Path("asins.json")
STATE_FILE = Path("state.json")
REQUEST_INTERVAL_SEC = 3  # Amazon側への配慮。短くしすぎない

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ja-JP,ja;q=0.9",
}


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def check_product(asin: str) -> dict:
    url = f"https://www.amazon.co.jp/dp/{asin}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # --- 在庫判定 ---
    cart_button = soup.select_one("#add-to-cart-button")
    availability_el = soup.select_one("#availability")
    availability_text = availability_el.get_text() if availability_el else ""
    out_of_stock_markers = ["現在お取り扱いできません", "在庫切れ", "一時的に在庫切れ"]
    in_stock = bool(cart_button) and not any(m in availability_text for m in out_of_stock_markers)

    # --- Prime/Amazon発送判定 ---
    merchant_info = soup.select_one("#merchant-info")
    seller_text = merchant_info.get_text() if merchant_info else ""
    is_amazon_ship = "Amazon.co.jp" in seller_text and ("発送" in seller_text or "販売" in seller_text)
    has_prime_badge = soup.select_one("i.a-icon-prime") is not None
    is_prime = is_amazon_ship or has_prime_badge

    title_el = soup.select_one("#productTitle")
    title = title_el.get_text(strip=True) if title_el else asin

    return {"in_stock": in_stock, "is_prime": is_prime, "title": title}


def main() -> None:
    asins = load_json(ASIN_FILE, [])
    state = load_json(STATE_FILE, {})

    for item in asins:
        asin = item["asin"]
        try:
            result = check_product(asin)
            state[asin] = {"in_stock": result["in_stock"], "is_prime": result["is_prime"]}
            print(f"[OK] {asin}: 在庫{'あり' if result['in_stock'] else 'なし'} / "
                  f"Prime{'○' if result['is_prime'] else '×'}")
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] {asin}: 取得失敗 {e}", file=sys.stderr)

        time.sleep(REQUEST_INTERVAL_SEC)

    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
