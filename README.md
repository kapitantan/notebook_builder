# notebook_builder
## 使用したもの
- google drive
- obsidian web cliper
- notebook LM enterprice
## 手順概要
- obsidianのvaultをgoogle drive上に作成する
- obsidian web cliperを使用して、youtubeを保存する
- google cloudからgoogle drive apiを呼んで、保存した内容を読み込む
- notebookを自動で作成する

## 実施メモ
認証する
- gcloud auth login
アクセストークンの設定
- export ACCESS_TOKEN=$(gcloud auth print-access-token)
main.pyの実行
- uv run main.py

google drive APIを呼ぶための認証
- gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform


