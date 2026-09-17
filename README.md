# ベイブレード在庫復活監視 → X自動投稿

Amazon.co.jpの商品ページを定期監視し、
「①在庫が復活 ②Amazon.co.jp発送(Prime対応)」の両方を満たした瞬間だけ、
アフィリエイトリンク付きでXに自動投稿するボットです。

## セットアップ手順(所要目安 20〜30分)

### 1. GitHubリポジトリを作る
1. github.com で新規リポジトリを作成(Private推奨)
2. このフォルダの中身(`monitor.py` `asins.json` `state.json` `requirements.txt` `.github/`)を全部アップロード
   - iPhoneなら「Working Copy」アプリや、GitHub Mobileアプリの「Add file」機能でアップロード可能

### 2. X Developer アカウントを作る
1. https://developer.x.com でアプリを作成
2. アプリの権限を **Read and Write** に設定(デフォルトはRead onlyなので要変更)
3. 権限変更後、**Access Token / Access Token Secret を再生成**すること(変更前のトークンはRead onlyのまま残るため)
4. 以下4つの値を控える
   - API Key / API Key Secret(Consumer Key/Secret)
   - Access Token / Access Token Secret

### 3. Amazonアソシエイトタグを確認
自分のアソシエイトID(例: `bey_bee-22` のような文字列)を控える

### 4. GitHub Secretsに登録
リポジトリの Settings → Secrets and variables → Actions → New repository secret で以下5つを登録

| Secret名 | 値 |
|---|---|
| AMAZON_ASSOCIATE_TAG | 自分のアソシエイトタグ |
| X_API_KEY | X APIのAPI Key |
| X_API_SECRET | X APIのAPI Key Secret |
| X_ACCESS_TOKEN | X APIのAccess Token |
| X_ACCESS_SECRET | X APIのAccess Token Secret |

### 5. 監視対象を編集
`asins.json` に監視したいベイブレード商品のASINを追加/削除する。
ASINは商品ページURLの `/dp/` の直後の10桁のコード。

### 6. 動作確認
GitHubのActionsタブ →「Beyblade Stock Monitor」→「Run workflow」で手動実行し、ログを確認。
iPhoneならGitHub Mobileアプリからも同じ操作が可能。

## 運用上の注意点

- **cron頻度**: `.github/workflows/monitor.yml` の `cron: "*/15 * * * *"` を編集すれば頻度変更可(GitHub Actionsの無料枠は月2,000分。15分おき・数ASINなら十分収まる)
- **Amazon側のブロックについて**: GitHub Actionsのようなデータセンター発のIPは、Amazonからアクセス頻度によってはCAPTCHAやブロック対象になることがあります。エラーが増えた場合は監視間隔を伸ばす、監視対象数を絞るなどの調整が必要です。
- **在庫判定の精度**: Amazonのページ構造は変更されることがあるため、誤検知(在庫ありなのに未検知、または逆)が出た場合は `monitor.py` のセレクタ(`#add-to-cart-button` 等)を見直してください。
- **アフィリエイトリンクの扱い**: このスクリプトは自分で取得した商品情報に、自分のアソシエイトタグを付与する形なので、他サイトのリンクを書き換える方式とは異なり規約上問題ありません。
