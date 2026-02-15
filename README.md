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
## 具体的手順
1. ○○

## 実施メモ
認証する（コンテナ内）
- gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform
- gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>

main.pyの実行
- docker compose up --build

