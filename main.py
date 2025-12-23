import sys
import queue
from playlist import get_playlist_video_urls
from worker import WorkerManager
from history import DownloadHistory
from config import load_settings
from startup_check import startup_check

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]

    settings = load_settings()
    ffmpeg_path = startup_check()

    if ffmpeg_path is None and not settings.get("audio_only") and not settings.get("video_only"):
        print("FFmpeg not available. Switching to audio-only mode.")
        settings["audio_only"] = True

    print("Extracting playlist...")
    video_urls = get_playlist_video_urls(playlist_url)

    history = DownloadHistory(settings["download_history"])
    pending = [url for url in video_urls if not history.is_done(url)]
    print(f"Total videos: {len(video_urls)} | Pending: {len(pending)}")

    if not pending:
        print("Nothing to download.")
        return

    task_queue = queue.Queue()
    for url in pending:
        task_queue.put(url)

    manager = WorkerManager(
        task_queue=task_queue,
        history=history,
        min_workers=settings["min_workers"],
        max_workers=settings["max_workers"],
        scale_interval=settings["scale_interval"],
        speed_threshold=settings["speed_threshold"],
        cpu_soft_limit=settings["cpu_soft_limit"],
        cpu_hard_limit=settings["cpu_hard_limit"],
        warmup_seconds=settings["warmup_seconds"],
        warmup_samples=settings["warmup_samples"],
        settings=settings,
        ffmpeg_path=ffmpeg_path
    )

    manager.start()
    task_queue.join()
    manager.stop()

    print("\nAll downloads completed!")

if __name__ == "__main__":
    main()
  
