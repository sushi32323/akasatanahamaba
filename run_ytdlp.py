import os
import sys
import yt_dlp
import requests

# GASから送られてきたURLを環境変数から取得
url = os.environ.get("VIDEO_URL")

def main():
    ydl_opts = {'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get('title')
        
        # --- ここで結果をGoogle側に送る ---
        # 例：GASのWebアプリURLに結果をPOSTする
        callback_url = "あなたのGASのURL"
        requests.post(callback_url, json={"title": title, "status": "completed"})

if __name__ == "__main__":
    main()
