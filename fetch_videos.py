import yt_dlp
import json
import re

CHANNELS = [
    "https://www.youtube.com/@rifajaslam",
    "https://www.youtube.com/@AlquranOpenCollegeSL",
    "https://www.youtube.com/@mishkathresearch7753",
    "https://www.youtube.com/@usthadmansoor",
    "https://www.youtube.com/@thafseerworldtafseer8529"
]

# Keywords to ensure the video is by Usthaz Mansoor (if the channel is mixed)
MANSOOR_KEYWORDS = [
    "mansoor", "மன்சூர்", "usthad", "usthaz", "usthaad", "உஸ்தாத்", "usthadh",
    "thafseer", "tafseer", "sura", "surah", "சூரா", "ஸூரா"
]

def is_mansoor_video(title, description, uploader):
    # If it's his own channel, assume all videos are his
    if "usthadmansoor" in uploader.lower().replace(" ", ""):
        return True
        
    text_to_check = (title + " " + description).lower()
    return any(keyword in text_to_check for keyword in MANSOOR_KEYWORDS)

def categorize_video(title, duration_str, uploader=""):
    title_lower = title.lower()
    uploader_lower = uploader.lower() if uploader else ""
    
    if "thafseerworld" in uploader_lower or "tafseer" in title_lower or "தப்ஸீர்" in title_lower or "குர்ஆன்" in title_lower or "quran" in title_lower or "surah" in title_lower or "சூரத்துல்" in title_lower or "சூரா" in title_lower or "ஸூரா" in title_lower:
        return "Tafseer & Quran"
    elif "khutbah" in title_lower or "ஜும்ஆ" in title_lower or "jummah" in title_lower or "jum'ah" in title_lower or "குத்பா" in title_lower:
        return "Jummah Khutbahs"
    elif "q&a" in title_lower or "கேள்வி" in title_lower or "பதில்" in title_lower or "question" in title_lower or "fatwa" in title_lower:
        return "Q&A"
    elif "history" in title_lower or "வரலாறு" in title_lower or "seerah" in title_lower or "ஸீரா" in title_lower:
        return "Islamic History"
    elif "ramadan" in title_lower or "ரமழான்" in title_lower or "நோன்பு" in title_lower or "fasting" in title_lower:
        return "Ramadan"
    elif "family" in title_lower or "குடும்பம்" in title_lower or "marriage" in title_lower or "திருமணம்" in title_lower or "பெண்கள்" in title_lower:
        return "Family & Marriage"
    
    # Try to categorize based on duration if it's short
    if duration_str:
        parts = duration_str.split(':')
        if len(parts) == 2: # mm:ss
            mins = int(parts[0])
            if mins < 5:
                return "Shorts"
    
    if "short" in title_lower or "#shorts" in title_lower:
        return "Shorts"
        
    return "General Lectures"

def format_duration(seconds):
    if not seconds: return None
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"

def fetch_videos():
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': False,
        'skip_download': True,
        'ignoreerrors': True
    }

    all_videos = []
    all_playlists = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for channel in CHANNELS:
            print(f"Fetching from {channel}...")
            
            # Fetch Videos, Shorts, and Playlists tabs
            for tab, force_category in [("/videos", None), ("/shorts", "Shorts"), ("/playlists", "Playlists")]:
                url_to_fetch = channel + tab
                print(f"  -> {url_to_fetch}")
                try:
                    info = ydl.extract_info(url_to_fetch, download=False)
                    
                    if info and 'entries' in info:
                        for entry in info['entries']:
                            if not entry: continue
                            
                            title = entry.get('title', '')
                            uploader = info.get('uploader', '') or entry.get('channel', '')
                            
                            if force_category == "Playlists":
                                playlist_info = {
                                    'id': entry.get('id'),
                                    'title': title,
                                    'url': entry.get('url'),
                                    'channel': entry.get('channel', uploader),
                                    'item_count': entry.get('playlist_count') or entry.get('item_count'),
                                    'thumbnail': next((t['url'] for t in entry.get('thumbnails', []) if t.get('url')), None)
                                }
                                all_playlists.append(playlist_info)
                            else:
                                desc = entry.get('description', '') or ''
                                # Get ALL videos
                                duration_seconds = entry.get('duration')
                                duration_str = format_duration(duration_seconds)
                                
                                # Determine category
                                cat = force_category if force_category else categorize_video(title, duration_str, uploader)
                                
                                vid_info = {
                                    'id': entry.get('id'),
                                    'title': title,
                                    'url': entry.get('url'),
                                    'channel': entry.get('channel', uploader),
                                    'duration': duration_str,
                                    'view_count': entry.get('view_count'),
                                    'thumbnail': next((t['url'] for t in entry.get('thumbnails', []) if t.get('url')), None),
                                    'category': cat,
                                    'upload_date': entry.get('upload_date')
                                }
                                all_videos.append(vid_info)
                except Exception as e:
                    print(f"Error fetching {url_to_fetch}: {e}")

    # Save to JS file so it works locally without a web server
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write("const VIDEO_DATA = ")
        json.dump(all_videos, f, indent=4, ensure_ascii=False)
        f.write(";\nconst PLAYLIST_DATA = ")
        json.dump(all_playlists, f, indent=4, ensure_ascii=False)
        f.write(";\n")

    print(f"\nSuccess! Total videos extracted: {len(all_videos)}")
    print(f"Total playlists extracted: {len(all_playlists)}")
    print("Data saved to data.js")

if __name__ == "__main__":
    fetch_videos()
