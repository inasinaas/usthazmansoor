import urllib.request
import urllib.error
import json

API_KEY = "AIzaSyBKyz0S5u8kbBWExU9-BkeKKANmFetRt3A"
video_id = "108ftr033ec"
url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={API_KEY}"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        print("Success:", response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print("Response body:", e.read().decode())
except Exception as e:
    print("Error:", e)
