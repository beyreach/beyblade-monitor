"""
ベイブレード関連商品限定 Amazon在庫復活監視 → X自動投稿

判定条件:
  1. カートボタンが存在し、かつ在庫切れ表記がない(在庫あり)
  2. 出品者が Amazon.co.jp 自身、または Prime バッジがある(Prime発送)
  両方を満たし、かつ「前回は在庫なしだった」場合のみ X に投稿する。

必要な環境変数(GitHub Secretsで渡す):
  AMAZON_ASSOCIATE_TAG : 自分のAmazonアソシエイトタグ
  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET : X API(OAuth1.0a, Read/Write権限)
"""

import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
import tweepy
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

AMAZON_TAG = os.environ.get("AMAZON_ASSOCIATE_TAG", "")


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

    return {"in_stock": in_stock, "is_prime": is_prime, "title": title, "url": url}


def build_affiliate_url(url: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{urlencode({'tag': AMAZON_TAG})}"


def post_tweet(text: str) -> None:
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_SECRET"],
    )
    client.create_tweet(text=text)


def main() -> None:
    asins = load_json(ASIN_FILE, [])
    state = load_json(STATE_FILE, {})

    for item in asins:
        asin = item["asin"]
        try:
            result = check_product(asin)
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] {asin}: 取得失敗 {e}", file=sys.stderr)
            time.sleep(REQUEST_INTERVAL_SEC)
            continue

        prev_in_stock = state.get(asin, {}).get("in_stock", False)

        if result["in_stock"] and result["is_prime"] and not prev_in_stock:
            affiliate_url = build_affiliate_url(result["url"])
            text = (
                f"復活！【Prime】{result['title'][:60]}\n"
                f"{affiliate_url}\n"
                f"#ベイブレードX #BEYBLADEX"
            )
            try:
                post_tweet(text)
                print(f"[POST] {asin}: {result['title']}")
            except Exception as e:  # noqa: BLE001
                print(f"[ERROR] {asin}: 投稿失敗 {e}", file=sys.stderr)

        state[asin] = {"in_stock": result["in_stock"], "is_prime": result["is_prime"]}
        time.sleep(REQUEST_INTERVAL_SEC)

    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
