# YouTube Downloader

A fully-featured, **multi-threaded YouTube downloader** with:

- Adaptive, CPU-aware worker scaling  
- Warm-up phase for accurate scaling decisions  
- Persistent download history  
- Safe filenames for all operating systems  
- Audio-only, video-only, or merged downloads  
- Automatic ffmpeg detection and optional download  
- Configurable settings via `settings.json`  
- Playlist support  

---

## Features

- **Multi-threaded downloads** with dynamic scaling based on CPU usage  
- **Warm-up phase** before scaling to estimate download speeds  
- **Persistent history** to prevent re-downloading videos  
- **Filesystem-safe filenames** for Windows, Linux, macOS  
- Supports `mp4`, `mkv`, `webm` merge formats  
- **Audio-only** or **video-only** download options  
- Automatic **ffmpeg detection and download** (Windows x64 example)  
- **Startup checks** for Python version, yt-dlp, ffmpeg, write permissions, and history file  

---

## Installation

1. **Clone repository:**

```bash
git clone https://github.com/yourusername/YouTubeDownloader.git
cd YouTubeDownloader
````

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

> Requirements include: `yt-dlp`, `psutil`

---

## Usage

```bash
python main.py <playlist_url>
```

* The program will create a **default `settings.json`** if it does not exist
* Performs a **startup check** to ensure everything is working
* Automatically switches to **audio-only** if ffmpeg is missing and auto-download is disabled

---

## Configuration

Edit `settings.json` to change downloader behavior:

| Setting                | Default                 | Description                                          |
| ---------------------- | ----------------------- | ---------------------------------------------------- |
| `min_workers`          | 2                       | Minimum number of worker threads                     |
| `max_workers`          | 8                       | Maximum number of worker threads                     |
| `scale_interval`       | 5.0                     | Interval (seconds) between scaling checks            |
| `speed_threshold`      | 0.10                    | Minimum average speed increase to scale up           |
| `cpu_soft_limit`       | 70.0                    | CPU usage % under which scaling up is allowed        |
| `cpu_hard_limit`       | 90.0                    | CPU usage % above which scaling down occurs          |
| `warmup_seconds`       | 15.0                    | Duration of warm-up phase before scaling             |
| `warmup_samples`       | 3                       | Number of samples during warm-up                     |
| `merge_format`         | `mp4`                   | Format for merged audio+video (`mp4`, `mkv`, `webm`) |
| `audio_only`           | false                   | Download audio only                                  |
| `video_only`           | false                   | Download video only                                  |
| `filename_replacement` | `_`                     | Character to replace illegal filename characters     |
| `auto_download_ffmpeg` | true                    | Automatically download ffmpeg if missing             |
| `ffmpeg_dir`           | `ffmpeg`                | Directory to store ffmpeg binary                     |
| `download_history`     | `download_history.json` | File to store download history                       |

---

## Limits / Current Restrictions

1. **FFmpeg auto-download** currently only supports **Windows 64-bit**.

   * Linux/macOS users need to install ffmpeg manually (`sudo apt install ffmpeg` or `brew install ffmpeg`).
2. **Maximum concurrent threads** limited by `max_workers`. Increasing too high may overload CPU/network.
3. **Filename length** is limited to 255 characters (filesystem safe).
4. **Merging only works** if ffmpeg is available; otherwise, the downloader will switch to audio-only mode automatically.
5. **Playlist size**: very large playlists (>1000 videos) may take long to queue; performance depends on CPU, network, and disk speed.
6. **Adaptive scaling** relies on `psutil.cpu_percent()` and network speed samples — may fluctuate in unstable networks.
7. **Audio-only conversion quality**: fixed at 192 kbps mp3 by default.

---

## Notes

* Persistent download history prevents re-downloading the same video.
* Safe filenames ensure compatibility with Windows, Linux, and macOS.
* Settings are **validated automatically** at startup and default values are created if missing.
* Multi-threaded downloading adapts dynamically based on CPU usage and download speed.

---

## Future Improvements

* GUI interface for live progress monitoring
* Cross-platform ffmpeg auto-download support (Linux/macOS)
* More flexible audio quality and format options
* Playlist resume support with partial downloads
