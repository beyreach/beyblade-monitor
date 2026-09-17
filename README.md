# ベイブレード在庫復活監視(通知専用)

Amazon.co.jpの商品ページを定期監視し、
「①在庫が復活 ②Amazon.co.jp発送(Prime対応)」の両方を満たした瞬間に、
`watcher.html`を開いている端末に通知します。X投稿機能はありません。

## セットアップ手順

### 1. GitHubリポジトリを作る(Public)
1. github.com で新規リポジトリを作成。**Public**にする(watcher.htmlが外部から state.json を読むため)
2. `monitor.py` `asins.json` `state.json` `requirements.txt` `.github/workflows/monitor.yml` をアップロード

これだけです。**GitHub Secretsの登録は不要**(X APIを使わないため)。

### 2. 動作確認
GitHubのActionsタブ →「Beyblade Stock Monitor」→「Run workflow」で手動実行し、ログを確認。
`state.json` が更新されていればOK。

### 3. 監視対象を編集
`asins.json` に監視したいベイブレード商品のASINを追加/削除する。

### 4. 通知を受け取る
`watcher.html` をiPhoneで開き、設定にGitHubユーザー名とリポジトリ名を入力。
このタブを開いている間、30秒おきに`state.json`をチェックし、
在庫復活(Prime対応)を検知したら通知音とブラウザ通知でお知らせします。

## 運用上の注意点

- **cron頻度**: `.github/workflows/monitor.yml` の `cron: "*/15 * * * *"` を編集すれば変更可(無料枠は月2,000分)
- **Amazon側のブロックについて**: GitHub ActionsのようなデータセンターIPは、アクセス頻度によってはCAPTCHAやブロック対象になることがあります。エラーが増えたら監視間隔を伸ばしてください
- **watcher.htmlはタブを開いている間だけ動作**します。閉じている間の検知結果も`state.json`には残るので、次に開いた時に最新状況は確認できます(ただし閉じていた間の「一瞬だけ復活した」通知は受け取れません)
