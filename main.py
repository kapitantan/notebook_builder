import requests
import os
from dotenv import load_dotenv
import json

import google.auth
import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

load_dotenv()
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
NOTEBOOK_URL  = "https://global-discoveryengine.googleapis.com/v1alpha/projects/37375335489/locations/global/notebooks"
NOTEBOOK_HEADERS  = {
        "Authorization":f"Bearer {ACCESS_TOKEN}",
        "Content-Type":"application/json"
    }
def get_notebook_name_list():
    return requests.get(url=NOTEBOOK_URL + ":listRecentlyViewed", headers=NOTEBOOK_HEADERS)


def create_notebook(youtube_title):
    payload = {
        "title":youtube_title,
    }
    r = requests.post(
        url=NOTEBOOK_URL,
        json=payload, 
        headers=NOTEBOOK_HEADERS
    )
    return r

def add_youtube_notebook(notebook_id, youtube_url):
    payload = {
        "userContents":[
            {"videoContent": {
                "youtubeUrl": youtube_url
                }
            }
        ]
    }
    r = requests.post(
        NOTEBOOK_URL + "/" + notebook_id  + "/sources:batchCreate" ,
        json=payload, 
        headers=NOTEBOOK_HEADERS
    )
    return r

def find_child_folder_id(service, parent_id: str, folder_name: str) -> str:
    # フォルダ検索（同名がある可能性があるので、最初の1件を採用）
    q = (
        f"'{parent_id}' in parents and "
        f"name = '{folder_name}' and "
        f"mimeType = 'application/vnd.google-apps.folder' and "
        f"trashed = false"
    )
    res = service.files().list(q=q, fields="files(id,name)", pageSize=10).execute()
    files = res.get("files", [])
    if not files:
        raise RuntimeError(f"Folder not found: {folder_name} (parent={parent_id})")
    return files[0]["id"]

def drive_service_readonly():
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    # Cloud Run / VM だと refresh が必要なことがあるので明示
    req = google.auth.transport.requests.Request()
    if not creds.valid:
        creds.refresh(req)
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def list_md_files_in_folder(service, folder_id: str):
    q = (
        f"'{folder_id}' in parents and "
        f"mimeType = 'text/markdown' and "
        f"trashed = false"
    )
    res = service.files().list(q=q, fields="files(id,name)", pageSize=1000).execute()
    return res.get("files", [])


def download_text_file(service, file_id: str) -> str:
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return fh.getvalue().decode("utf-8", errors="replace")


def main():
    # 作成済みnotebook名を取得
    r = get_notebook_name_list()
    data = json.loads(r.text)

    title_list = []
    for v in data["notebooks"]:
        title_list.append(v["title"])
    print(title_list)

    # google drive上のmdファイルを探索
    svc = drive_service_readonly()
    obsidian_id = find_child_folder_id(svc, "root", "obsidian")
    youtube_id = find_child_folder_id(svc, obsidian_id, "5_youtube")

    md_files = list_md_files_in_folder(svc, youtube_id)
    print("md files:", [f["name"] for f in md_files])

    # 先頭ファイルの本文を取得（本文そのものはログ出力しない）
    if md_files:
        content = download_text_file(svc, md_files[0]["id"])
        print("first md chars:", len(content))

    # r = create_notebook("世界初のコンピュータの写真。写っている女性は何者なのか？143")
    # data = json.loads(r.text)
    # print(data)
    # notebook_id = data["notebookId"] 
    # r = add_youtube_notebook(notebook_id, "https://www.youtube.com/watch?v=55_h0tTezyU&list=WL&index=2&t=54s")
    # print(r.text)
    


if __name__ == "__main__":
    main()
