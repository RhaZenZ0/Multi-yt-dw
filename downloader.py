from yt_dlp import YoutubeDL
import time
from utils import sanitize_filename

def download_video(url: str, settings: dict, ffmpeg_path: str = None):
    start = time.time()
    downloaded_bytes = 0

    def progress_hook(d):
        nonlocal downloaded_bytes
        if d.get("status") == "downloading":
            downloaded_bytes = d.get("downloaded_bytes", 0)

    with YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        title = info_dict.get("title", "video")

    safe_name = sanitize_filename(title, settings.get("filename_replacement", "_"))
    ext = settings.get("merge_format") or ("mp3" if settings.get("audio_only") else "mp4")
    outtmpl = f"{safe_name}.{ext}"

    ydl_opts = {
        "progress_hooks": [progress_hook],
        "quiet": settings.get("quiet", True),
        "no_warnings": True,
        "outtmpl": outtmpl,
    }

    if settings.get("audio_only"):
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": ext,
            "preferredquality": "192",
        }]
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path
    elif settings.get("video_only"):
        ydl_opts["format"] = "bestvideo/best"
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"
        ydl_opts["merge_output_format"] = ext
        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    duration = time.time() - start
    return downloaded_bytes, duration
  
