import os
import json
import yt_dlp
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# GitHubのSecretsから情報を受け取る
folder_id = os.environ.get("GDRIVE_FOLDER_ID")
service_account_info = json.loads(os.environ.get("GDRIVE_SERVICE_ACCOUNT_JSON"))
video_url = os.environ.get("VIDEO_URL")

def upload_to_drive(file_path):
    # Googleドライブへの認証
    creds = service_account.Credentials.from_service_account_info(service_account_info)
    service = build('drive', 'v3', credentials=creds)
    
    # アップロードの設定
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)
    
    print(f"Uploading {file_path} to Google Drive...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File ID: {file.get('id')}")

def main():
    if not video_url:
        print("Error: No URL provided.")
        return

    # yt-dlpの設定（動画のタイトルをファイル名にする）
    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # mp4を優先
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ダウンロード実行
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Googleドライブにアップロード
            upload_to_drive(filename)
            
            # 終わったらGitHub上のファイルを消して整理
            os.remove(filename)
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
