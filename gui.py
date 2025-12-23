import sys
import queue
import threading
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QComboBox, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, QTimer

from worker import WorkerManager
from history import DownloadHistory
from config import load_settings
from startup_check import startup_check
from playlist import get_playlist_video_urls

class DownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.resize(600, 400)
        self.settings = load_settings()
        self.ffmpeg_path = startup_check()
        self.history = DownloadHistory(self.settings["download_history"])
        self.task_queue = queue.Queue()
        self.manager = None
        self.video_urls = []

        # --- UI Elements ---
        layout = QVBoxLayout()

        self.url_label = QLabel("Playlist URL:")
        self.url_input = QLineEdit()
        self.start_btn = QPushButton("Start Download")
        self.progress_bar = QProgressBar()
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)

        # Options
        self.audio_only_cb = QCheckBox("Audio Only")
        self.video_only_cb = QCheckBox("Video Only")
        self.merge_combo = QComboBox()
        self.merge_combo.addItems(["mp4", "mkv", "webm"])
        self.merge_combo.setCurrentText(self.settings.get("merge_format", "mp4"))

        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.audio_only_cb)
        layout.addWidget(self.video_only_cb)
        layout.addWidget(QLabel("Merge Format:"))
        layout.addWidget(self.merge_combo)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_text)

        self.setLayout(layout)

        # Signals
        self.start_btn.clicked.connect(self.start_download)

        # Timer for GUI updates
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start()

        self.completed_count = 0

    def log(self, message):
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.log("Please enter a playlist URL.")
            return

        self.log(f"Extracting playlist: {url}")
        threading.Thread(target=self.prepare_download, args=(url,), daemon=True).start()

    def prepare_download(self, url):
        try:
            self.video_urls = get_playlist_video_urls(url)
        except Exception as e:
            self.log(f"Error extracting playlist: {e}")
            return

        pending = [v for v in self.video_urls if not self.history.is_done(v)]
        total = len(pending)
        if total == 0:
            self.log("All videos already downloaded.")
            return

        self.progress_bar.setMaximum(total)
        self.completed_count = 0

        # Update settings from GUI
        self.settings["audio_only"] = self.audio_only_cb.isChecked()
        self.settings["video_only"] = self.video_only_cb.isChecked()
        self.settings["merge_format"] = self.merge_combo.currentText() if not (self.settings["audio_only"] or self.settings["video_only"]) else None

        for v in pending:
            self.task_queue.put(v)

        self.manager = WorkerManager(
            task_queue=self.task_queue,
            history=self.history,
            min_workers=self.settings["min_workers"],
            max_workers=self.settings["max_workers"],
            scale_interval=self.settings["scale_interval"],
            speed_threshold=self.settings["speed_threshold"],
            cpu_soft_limit=self.settings["cpu_soft_limit"],
            cpu_hard_limit=self.settings["cpu_hard_limit"],
            warmup_seconds=self.settings["warmup_seconds"],
            warmup_samples=self.settings["warmup_samples"],
            settings=self.settings,
            ffmpeg_path=self.ffmpeg_path
        )
        threading.Thread(target=self.run_manager, daemon=True).start()

    def run_manager(self):
        self.manager.start()
        self.task_queue.join()
        self.manager.stop()
        self.log("All downloads completed!")

    def update_gui(self):
        if not self.video_urls:
            return
        done = sum([self.history.is_done(v) for v in self.video_urls])
        self.completed_count = done
        self.progress_bar.setValue(done)
        self.log(f"Progress: {done}/{len(self.video_urls)} videos downloaded")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DownloaderGUI()
    gui.show()
    sys.exit(app.exec())
    
