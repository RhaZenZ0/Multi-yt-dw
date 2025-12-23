import json
import os
from typing import Any, Dict

CONFIG_FILE = "settings.json"

DEFAULT_SETTINGS: Dict[str, Any] = {
    # Worker limits
    "min_workers": 2,
    "max_workers": 8,

    # Adaptive scaling
    "scale_interval": 5.0,
    "speed_threshold": 0.10,
    "cpu_soft_limit": 70.0,
    "cpu_hard_limit": 90.0,

    # Warm-up phase
    "warmup_seconds": 15.0,
    "warmup_samples": 3,

    # yt-dlp options
    "format": "best",
    "quiet": True,

    # Paths
    "download_history": "download_history.json",

    # Video/audio options
    "merge_format": "mp4",
    "audio_only": False,
    "video_only": False,
    "filename_replacement": "_",

    # FFmpeg auto-download
    "auto_download_ffmpeg": True,
    "ffmpeg_dir": "ffmpeg",
}


def validate_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    settings["min_workers"] = max(1, int(settings.get("min_workers", 2)))
    settings["max_workers"] = max(settings["min_workers"], int(settings.get("max_workers", 8)))
    settings["scale_interval"] = float(settings.get("scale_interval", 5.0))
    settings["speed_threshold"] = float(settings.get("speed_threshold", 0.1))
    settings["cpu_soft_limit"] = float(settings.get("cpu_soft_limit", 70.0))
    settings["cpu_hard_limit"] = float(settings.get("cpu_hard_limit", 90.0))
    if settings["cpu_soft_limit"] >= settings["cpu_hard_limit"]:
        settings["cpu_soft_limit"] = max(0.0, settings["cpu_hard_limit"] - 5.0)

    settings["warmup_seconds"] = max(0.0, float(settings.get("warmup_seconds", 15.0)))
    settings["warmup_samples"] = max(1, int(settings.get("warmup_samples", 3)))

    settings["format"] = str(settings.get("format", "best"))
    settings["quiet"] = bool(settings.get("quiet", True))
    settings["download_history"] = str(settings.get("download_history", "download_history.json"))

    merge_format = str(settings.get("merge_format", "mp4")).lower()
    if merge_format not in {"mp4", "mkv", "webm"}:
        merge_format = "mp4"
    settings["merge_format"] = merge_format

    settings["audio_only"] = bool(settings.get("audio_only", False))
    settings["video_only"] = bool(settings.get("video_only", False))
    if settings["audio_only"] or settings["video_only"]:
        settings["merge_format"] = None

    settings["filename_replacement"] = str(settings.get("filename_replacement", "_"))[0]
    settings["auto_download_ffmpeg"] = bool(settings.get("auto_download_ffmpeg", True))
    settings["ffmpeg_dir"] = str(settings.get("ffmpeg_dir", "ffmpeg"))

    return settings


def save_settings(settings: Dict[str, Any], path: str = CONFIG_FILE):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
    os.replace(tmp, path)


def load_settings(path: str = CONFIG_FILE) -> Dict[str, Any]:
    if not os.path.exists(path):
        save_settings(DEFAULT_SETTINGS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
    except Exception:
        user_settings = {}

    merged = DEFAULT_SETTINGS.copy()
    merged.update(user_settings)
    merged = validate_settings(merged)
    save_settings(merged, path)
    return merged
  
