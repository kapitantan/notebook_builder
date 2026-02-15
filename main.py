import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
URL = "https://global-discoveryengine.googleapis.com/v1alpha/projects/37375335489/locations/global/notebooks"
HEADERS = {
        "Authorization":f"Bearer {ACCESS_TOKEN}",
        "Content-Type":"application/json"
    }

def create_notebook(youtube_title):
    payload = {
        "title":youtube_title,
    }
    r = requests.post(
        url=URL,
        json=payload, 
        headers=HEADERS
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
        URL + "/" + notebook_id  + "/sources:batchCreate" ,
        json=payload, 
        headers=HEADERS
    )
    return r

def get_notebook_name_list():
    r = requests.get(
        url=URL+":listRecentlyViewed",
        headers=HEADERS
    )
    return r

def main():
    # 作成済みnotebook名を取得
    r = get_notebook_name_list()
    print(r.text)
    data = json.loads(r.text)

    title_list = []
    for v in data["notebooks"]:
        title_list.append(v["title"])
    print(title_list)

    # google drive上のmdファイルを探索

    # r = create_notebook("世界初のコンピュータの写真。写っている女性は何者なのか？143")
    # data = json.loads(r.text)
    # print(data)
    # notebook_id = data["notebookId"] 
    # r = add_youtube_notebook(notebook_id, "https://www.youtube.com/watch?v=55_h0tTezyU&list=WL&index=2&t=54s")
    # print(r.text)
    


if __name__ == "__main__":
    main()
