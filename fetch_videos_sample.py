import yt_dlp
import json

CHANNELS = [
    "https://www.youtube.com/@rifajaslam",
    "https://www.youtube.com/@AlquranOpenCollegeSL",
    "https://www.youtube.com/@mishkathresearch7753",
    "https://www.youtube.com/@usthadmansoor"
]

ydl_opts = {
    'extract_flat': 'in_playlist',
    'playlistend': 30, # fetch only first 30 for testing
    'quiet': True,
    'skip_download': True,
    'ignoreerrors': True
}

all_videos = []

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for channel in CHANNELS:
        print(f"Fetching from {channel}...")
        try:
            info = ydl.extract_info(channel, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        title = entry.get('title', '')
                        desc = entry.get('description', '') or ''
                        # Filter for Mansoor if needed, or we just grab all and filter later.
                        # For @usthadmansoor, all are probably his.
                        # For others, we'll check later.
                        vid_info = {
                            'id': entry.get('id'),
                            'title': title,
                            'url': entry.get('url'),
                            'channel': info.get('uploader'),
                            'duration': entry.get('duration'),
                            'view_count': entry.get('view_count'),
                            'thumbnail': next((t['url'] for t in entry.get('thumbnails', []) if t.get('url')), None)
                        }
                        all_videos.append(vid_info)
        except Exception as e:
            print(f"Error fetching {channel}: {e}")

with open('videos_sample.json', 'w', encoding='utf-8') as f:
    json.dump(all_videos, f, indent=4, ensure_ascii=False)

print(f"Total videos fetched: {len(all_videos)}")
