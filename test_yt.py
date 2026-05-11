import yt_dlp
import json

def test():
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'ignoreerrors': True,
        'extract_flat': False
    }
    url = "https://www.youtube.com/watch?v=108ftr033ec"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info:
            print(f"Timestamp: {info.get('timestamp')}")
            print(f"Upload Date: {info.get('upload_date')}")

test()
