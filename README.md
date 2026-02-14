認証する
- gcloud auth login
アクセストークンの設定
- export ACCESS_TOKEN=$(gcloud auth print-access-token)
main.pyの実行
- uv run main.py

google drive APIを呼ぶための認証
- gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive.readonly,https://www.googleapis.com/auth/cloud-platform


