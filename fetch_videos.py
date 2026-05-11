import yt_dlp
import json
import re
import os
import urllib.request
import urllib.parse
from datetime import datetime

API_KEY = "AIzaSyBKyz0S5u8kbBWExU9-BkeKKANmFetRt3A"

CHANNELS = [
    "https://www.youtube.com/@rifajaslam",
    "https://www.youtube.com/@AlquranOpenCollegeSL",
    "https://www.youtube.com/@mishkathresearch7753",
    "https://www.youtube.com/@usthadmansoor",
    "https://www.youtube.com/@thafseerworldtafseer8529"
]

MANSOOR_KEYWORDS = [
    "mansoor", "மன்சூர்", "usthad", "usthaz", "usthaad", "உஸ்தாத்", "usthadh",
    "thafseer", "tafseer", "sura", "surah", "சூரா", "ஸூரா"
]

def is_mansoor_video(title, description, uploader):
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
    if duration_str:
        parts = duration_str.split(':')
        if len(parts) == 2:
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

def parse_iso8601_duration(duration_str):
    # Example: PT1H2M10S or PT5M30S
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration_str)
    if not match:
        return 0
    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0
    seconds = int(match.group(3)) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

def fetch_api_details(video_ids):
    api_url = "https://www.googleapis.com/youtube/v3/videos"
    results = {}
    
    # Process in chunks of 50 (max allowed by API)
    chunk_size = 50
    for i in range(0, len(video_ids), chunk_size):
        chunk = video_ids[i:i+chunk_size]
        ids_str = ",".join(chunk)
        
        url = f"{api_url}?part=snippet,contentDetails,statistics&id={ids_str}&key={API_KEY}"
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                
                for item in data.get('items', []):
                    vid = item['id']
                    snippet = item.get('snippet', {})
                    content_details = item.get('contentDetails', {})
                    statistics = item.get('statistics', {})
                    
                    published_at = snippet.get('publishedAt') # e.g., '2023-01-01T12:00:00Z'
                    timestamp = None
                    if published_at:
                        # python 3.11 fromisoformat handles Z, but let's be safe
                        dt_str = published_at.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(dt_str)
                        timestamp = int(dt.timestamp())
                        
                    duration_str = content_details.get('duration')
                    duration_secs = parse_iso8601_duration(duration_str) if duration_str else None
                    
                    view_count = int(statistics.get('viewCount', 0))
                    
                    results[vid] = {
                        'timestamp': timestamp,
                        'duration_secs': duration_secs,
                        'view_count': view_count,
                        'thumbnails': snippet.get('thumbnails', {})
                    }
        except Exception as e:
            print(f"API Error fetching chunk: {e}")
            
    return results

def fetch_videos():
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': False,
        'skip_download': True,
        'ignoreerrors': True
    }

    all_videos = []
    all_playlists = []
    
    # 1. Fetch initial list via yt-dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for channel in CHANNELS:
            print(f"Fetching from {channel}...")
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
                            vid_id = entry.get('id')
                            
                            if force_category == "Playlists":
                                playlist_info = {
                                    'id': vid_id,
                                    'title': title,
                                    'url': entry.get('url'),
                                    'channel': entry.get('channel', uploader),
                                    'item_count': entry.get('playlist_count') or entry.get('item_count'),
                                    'thumbnail': next((t['url'] for t in entry.get('thumbnails', []) if t.get('url')), None)
                                }
                                all_playlists.append(playlist_info)
                            else:
                                duration_seconds = entry.get('duration')
                                duration_str = format_duration(duration_seconds)
                                cat = force_category if force_category else categorize_video(title, duration_str, uploader)
                                
                                vid_info = {
                                    'id': vid_id,
                                    'title': title,
                                    'url': entry.get('url'),
                                    'channel': entry.get('channel', uploader),
                                    'duration': duration_str,
                                    'view_count': entry.get('view_count'),
                                    'thumbnail': next((t['url'] for t in entry.get('thumbnails', []) if t.get('url')), None),
                                    'category': cat,
                                    'timestamp': None # Will be filled by API
                                }
                                all_videos.append(vid_info)
                except Exception as e:
                    print(f"Error fetching {url_to_fetch}: {e}")

    # 2. Enrich video data with YouTube API
    video_ids = [v['id'] for v in all_videos if v['id']]
    # Remove duplicates
    video_ids = list(dict.fromkeys(video_ids))
    
    print(f"\nFetching exact timestamps via YouTube API for {len(video_ids)} videos...")
    api_details = fetch_api_details(video_ids)
    
    # 3. Update the list
    for v in all_videos:
        vid = v['id']
        if vid in api_details:
            details = api_details[vid]
            v['timestamp'] = details['timestamp']
            
            # API gives more accurate views and sometimes thumbnails
            if details['view_count'] is not None:
                v['view_count'] = details['view_count']
                
            if details['duration_secs']:
                v['duration'] = format_duration(details['duration_secs'])
                
            # If standard thumbnail is missing, use API's
            if not v['thumbnail']:
                thumbnails = details['thumbnails']
                if 'high' in thumbnails:
                    v['thumbnail'] = thumbnails['high']['url']
                elif 'default' in thumbnails:
                    v['thumbnail'] = thumbnails['default']['url']

    # 4. Save to JS file so it works locally without a web server
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
