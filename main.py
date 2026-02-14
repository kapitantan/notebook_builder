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

def main():
    r = create_notebook("youtube")
    data = json.loads(r.text)
    print(data)
    notebook_id = data["notebookId"] 
    r = add_youtube_notebook(notebook_id, "https://www.youtube.com/watch?v=55_h0tTezyU&list=WL&index=2&t=54s")
    print(r.text)
    


if __name__ == "__main__":
    main()
