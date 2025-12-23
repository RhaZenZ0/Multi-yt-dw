import sys
import shutil
import os
import platform
import urllib.request
import zipfile
from config import load_settings, DEFAULT_SETTINGS, save_settings

def download_ffmpeg(ffmpeg_dir: str) -> str:
    os.makedirs(ffmpeg_dir, exist_ok=True)
    ffmpeg_exec = os.path.join(ffmpeg_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    if os.path.exists(ffmpeg_exec):
        return ffmpeg_exec
    system = platform.system()
    arch = platform.machine()
    print("Downloading ffmpeg for your system...")
    if system == "Windows" and arch.endswith("64"):
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
        urllib.request.urlretrieve(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(ffmpeg_dir)
        for root, dirs, files in os.walk(ffmpeg_dir):
            if "ffmpeg.exe" in files:
                return os.path.join(root, "ffmpeg.exe")
        raise FileNotFoundError("ffmpeg binary not found after extraction")
    else:
        print(f"Auto ffmpeg download not supported on {system}/{arch}")
        return None

def startup_check(settings_path: str = "settings.json") -> str:
    if not os.path.exists(settings_path):
        print(f"[INFO] Creating default settings: {settings_path}")
        save_settings(DEFAULT_SETTINGS, settings_path)

    settings = load_settings(settings_path)
    ffmpeg_path = shutil.which("ffmpeg")
    all_ok = True

    if sys.version_info < (3, 10):
        print(f"[ERROR] Python 3.10+ required, found {sys.version}")
        all_ok = False
    else:
        print(f"[OK] Python version: {sys.version}")

    try:
        import yt_dlp
        print("[OK] yt-dlp installed")
    except ImportError:
        print("[ERROR] yt-dlp not installed!")
        all_ok = False

    if ffmpeg_path:
        print(f"[OK] ffmpeg found: {ffmpeg_path}")
    elif settings.get("auto_download_ffmpeg"):
        try:
            ffmpeg_path = download_ffmpeg(settings.get("ffmpeg_dir"))
            print(f"[OK] ffmpeg downloaded: {ffmpeg_path}")
        except Exception as e:
            print(f"[ERROR] ffmpeg download failed: {e}")
            ffmpeg_path = None
            all_ok = False
    else:
        print("[WARNING] ffmpeg not found, merging may fail")
        ffmpeg_path = None

    try:
        test_file = "._test_write.tmp"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("[OK] Write permissions verified")
    except Exception as e:
        print(f"[ERROR] Write permission issue: {e}")
        all_ok = False

    try:
        hist_file = settings.get("download_history", "download_history.json")
        if os.path.exists(hist_file):
            with open(hist_file, "r+") as f:
                pass
        else:
            with open(hist_file, "w") as f:
                f.write("{}")
        print("[OK] Download history accessible")
    except Exception as e:
        print(f"[ERROR] History file issue: {e}")
        all_ok = False

    if all_ok:
        print("\n[STARTUP CHECK PASSED]\n")
    else:
        print("\n[STARTUP CHECK WARNING]\n")

    return ffmpeg_path
  
