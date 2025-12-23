from yt_dlp import YoutubeDL

def get_playlist_video_urls(playlist_url: str):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        entries = info.get("entries", [])
        urls = [entry["url"] for entry in entries if entry.get("url")]
        return urls
      
