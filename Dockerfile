FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# 先にrequirementsだけコピー（キャッシュ効く）
COPY requirements.txt .

# 依存インストール
RUN uv pip install --system -r requirements.txt

# アプリ本体
COPY . .

CMD ["python", "main.py"]
