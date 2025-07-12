from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re, os, time, requests
from dotenv import load_dotenv
import schedule
from rich import print
from pathlib import Path
import pandas as pd
import datetime as dt

load_dotenv()

URL        = os.getenv("ITEM_URL")
BASELINE   = float(os.getenv("BASELINE"))
THRESHOLD  = float(os.getenv("THRESHOLD"))
SLACK_URL  = os.getenv("SLACK_WEBHOOK")

def fetch_price(url: str) -> float:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        soup = BeautifulSoup(page.content(), "lxml")

        # ❶ 価格タグをざっくり拾う
        tag = soup.select_one("span.a-price > span.a-offscreen")
        if not tag:
            raise ValueError("Price tag not found!")
        price_txt = tag.get_text()        # 例：'￥1,980'
        print(price_txt[:200])    # 先頭200文字だけ覗く
        price = float(price_txt.replace("￥", "").replace(",", ""))

        browser.close()
        return price

def notify(price: float, diff: float) -> None:
    payload = {
        "text": f"💰 {diff:.1f}%値下げ！ いま ¥{price:,.0f}\n<{URL}|商品ページはこちら>"
    }
    r = requests.post(SLACK_URL, json=payload, timeout=10)
    print(f"[green]Slack status:[/green] {r.status_code}")

def save_history(price: float) -> None:
    """取得した価格を CSV に追記する"""
    df = pd.DataFrame(
        [[dt.datetime.now(), price]],
        columns=["ts", "price"]
    )
    file = Path("prices.csv")
    df.to_csv(
        file,
        mode="a",
        header=not file.exists(),  # ファイルが無い時だけヘッダーを付ける
        index=False,
        encoding="utf-8-sig"
    )

def job() -> None:
    try:
        price = fetch_price(URL)
    except Exception as e:
        print(f"[red]ERROR fetch_price:[/red] {e}")
        return
    save_history(price)
    diff = -100 * (price - BASELINE) / BASELINE
    print(f"[yellow]Now:[/yellow] ¥{price:,.0f} / baseline ¥{BASELINE:,.0f} / diff {diff:.2f}%")

    if diff >= THRESHOLD:
        notify(price, diff)

# 10 分ごとに回す
schedule.every(10).minutes.do(job)

if __name__ == "__main__":
    print("[bold green]Start tracking...[/bold green]")
    job()  # 起動直後に 1 回実行
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    url = "https://www.amazon.co.jp/%E3%83%AD%E3%82%A4%E3%83%A4%E3%83%AB%E3%82%AB%E3%83%8A%E3%83%B3-%EF%BC%88%E5%AE%A4%E5%86%85%E3%81%A7%E7%94%9F%E6%B4%BB%E3%81%99%E3%82%8B%E7%8C%AB%E5%B0%82%E7%94%A8%E3%83%95%E3%83%BC%E3%83%89-%E6%88%90%E7%8C%AB%E7%94%A8%EF%BC%892kg-%E8%B6%85%E9%AB%98%E6%B6%88%E5%8C%96%E6%80%A7%E3%82%BF%E3%83%B3%E3%83%91%E3%82%AF%E3%82%92%E9%85%8D%E5%90%88-%E3%82%AB%E3%83%AD%E3%83%AA%E3%83%BC%E5%90%AB%E6%9C%89%E9%87%8F%E3%82%92%E9%81%A9%E5%88%87/dp/B0DR9BXLNW/ref=sr_1_1_sspa?crid=P4WB6F8DUWIH&dib=eyJ2IjoiMSJ9.h_Fm9vkt2J2rksaWnTP0HHMSobphPapkcuMRiQWXvLDguqmKmJ3O9DmG4RKu_qgYxyLjpkbmJdmUDia4JDFnEpGCFwv4cDOLlSN6tU4aCT5QKBOjjv0V6NkMU4hgOStZEE3qVlCzFhaIsK-dKx3goaRJqls2lTILlRqpgBN-81R4Pz_kPb6e5EgmsKtG8NECw4ucnjb6D5XZlzSkBXoPaAPVzya6ScilbhN396fHP_SiSXcnyuF3rSClrWLBzCzqXnnIsFgxfratPOvM6PnISwAsiDakz9fwC57kWtg7Pb8.NJ36dIu7mnK5PMPXRnvnfkTSD1wry9BBUpAI1wOqGfQ&dib_tag=se&keywords=%E3%83%AD%E3%82%A4%E3%83%A4%E3%83%AB%E3%82%AB%E3%83%8A%E3%83%B3+%E7%8C%AB&qid=1752042188&sprefix=roi%2Caps%2C191&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1"  # 好きな商品ページに置き換え
    print(fetch_price(url))

from pathlib import Path
import pandas as pd
import datetime as dt
# ↑ すでに import がある行に続けて書き足してもOK


# 既存の job() の中で fetch_price が終わった直後に呼び出す
def job() -> None:
    try:
        price = fetch_price(URL)
    except Exception as e:
        print(f"[red]ERROR fetch_price:[/red] {e}")
        return

    save_history(price)          # ★これを追加
    diff = -100 * (price - BASELINE) / BASELINE
    ...



