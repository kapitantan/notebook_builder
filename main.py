import requests
import json
import re

import google.auth
import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

NOTEBOOK_URL  = "https://global-discoveryengine.googleapis.com/v1alpha/projects/37375335489/locations/global/notebooks"


def get_notebook_headers():
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    req = google.auth.transport.requests.Request()
    if not creds.valid:
        creds.refresh(req)
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }


def get_notebook_name_list():
    return requests.get(url=NOTEBOOK_URL + ":listRecentlyViewed", headers=get_notebook_headers())


def create_notebook(youtube_title):
    payload = {
        "title":youtube_title,
    }
    r = requests.post(
        url=NOTEBOOK_URL,
        json=payload, 
        headers=get_notebook_headers()
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
        headers=get_notebook_headers()
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


def parse_frontmatter_metadata(md_text: str):
    # 先頭 frontmatter の title / source を抽出する
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", md_text, flags=re.DOTALL)
    if not m:
        return None, None

    frontmatter = m.group(1)
    title = None
    source = None
    for line in frontmatter.splitlines():
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key == "title":
            title = value
        elif key == "source":
            source = value
    return title, source


def main():
    # 作成済みnotebook名を取得
    r = get_notebook_name_list()
    data = json.loads(r.text)

    title_set = set()
    for v in data["notebooks"]:
        title = v.get("title")
        if title:
            title_set.add(title)
    print("existing notebooks:", sorted(title_set))

    # google drive上のmdファイルを探索
    svc = drive_service_readonly()
    obsidian_id = find_child_folder_id(svc, "root", "obsidian")
    youtube_id = find_child_folder_id(svc, obsidian_id, "5_youtube")

    md_files = list_md_files_in_folder(svc, youtube_id)
    print("md files:", [f["name"] for f in md_files])

    for md_file in md_files:
        content = download_text_file(svc, md_file["id"])
        title, source = parse_frontmatter_metadata(content)

        if not title or not source:
            print(f"skip {md_file['name']}: title/source not found")
            continue
        if "youtube.com" not in source and "youtu.be" not in source:
            print(f"skip {md_file['name']}: source is not youtube url")
            continue
        if title in title_set:
            print(f"skip {md_file['name']}: notebook already exists ({title})")
            continue

        create_res = create_notebook(title)
        if not create_res.ok:
            print(f"create failed {md_file['name']}: status={create_res.status_code} body={create_res.text}")
            continue

        create_data = create_res.json()
        notebook_id = create_data.get("notebookId")
        if not notebook_id:
            print(f"create failed {md_file['name']}: notebookId not found in response")
            continue

        add_res = add_youtube_notebook(notebook_id, source)
        if not add_res.ok:
            print(f"source add failed {md_file['name']}: status={add_res.status_code} body={add_res.text}")
            continue

        title_set.add(title)
        print(f"created notebook: {title} ({notebook_id})")
    


if __name__ == "__main__":
    main()
