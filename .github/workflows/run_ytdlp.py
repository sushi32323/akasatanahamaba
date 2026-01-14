import os
import json
import yt_dlp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GitHubのSecretsから環境変数を取得
folder_id = os.environ.get("GDRIVE_FOLDER_ID")
service_account_info = json.loads(os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON"))
video_url = os.environ.get("VIDEO_URL")
cookies_content = os.environ.get("YOUTUBE_COOKIES")

def upload_to_drive(file_path):
    """Googleドライブにファイルをアップロードする"""
    try:
        creds = service_account.Credentials.from_service_account_info(service_account_info)
        service = build('drive', 'v3', credentials=creds)
        
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        print(f"Uploading {file_path} to Google Drive...")
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Success! File ID: {file.get('id')}")
    except Exception as e:
        print(f"Upload failed: {e}")

def main():
    if not video_url:
        print("Error: No URL provided.")
        return

    # クッキー情報をファイルに書き出す
    if cookies_content:
        with open("cookies.txt", "w") as f:
            f.write(cookies_content)
        print("Cookies loaded.")

    # yt-dlpの設定
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'cookiefile': 'cookies.txt' if cookies_content else None,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Starting download: {video_url}")
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # ファイルが存在するか確認してアップロード
            if os.path.exists(filename):
                upload_to_drive(filename)
                os.remove(filename) # 終わったらGitHub上のファイルを削除
            else:
                # 稀に拡張子が自動で変わる場合があるため、カレントディレクトリのmp4を探す
                files = [f for f in os.listdir('.') if f.endswith('.mp4')]
                if files:
                    upload_to_drive(files[0])
                    os.remove(files[0])

    except Exception as e:
        print(f"An error occurred during process: {e}")

if __name__ == "__main__":
    main()
