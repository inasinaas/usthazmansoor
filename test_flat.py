import yt_dlp
import json

def test():
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'skip_download': True,
        'ignoreerrors': True
    }
    url = "https://www.youtube.com/@usthadmansoor/videos"
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if info and 'entries' in info:
            entries = list(info['entries'])
            if entries:
                first = entries[0]
                print(json.dumps(first, indent=4))

test()
