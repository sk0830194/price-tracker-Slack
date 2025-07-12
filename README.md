# 商品価格トラッカー（Slack 通知付き）
## セットアップ

```bash
pip install -r requirements.txt
playwright install   # 初回のみ
cp .env.example .env # 値を埋める
python price_tracker.py

BASELINE … 比較基準価格

THRESHOLD … 値下げ何％で通知するか
