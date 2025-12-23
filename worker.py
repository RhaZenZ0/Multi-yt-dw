import threading
import queue
from downloader import download_video
from utils import get_cpu_percent
import time

STOP = object()

class WorkerManager:
    def __init__(self, task_queue: queue.Queue, history,
                 min_workers=2, max_workers=8,
                 scale_interval=5.0, speed_threshold=0.1,
                 cpu_soft_limit=70.0, cpu_hard_limit=90.0,
                 warmup_seconds=15.0, warmup_samples=3,
                 settings=None, ffmpeg_path=None):
        self.task_queue = task_queue
        self.history = history
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.scale_interval = scale_interval
        self.speed_threshold = speed_threshold
        self.cpu_soft_limit = cpu_soft_limit
        self.cpu_hard_limit = cpu_hard_limit
        self.warmup_seconds = warmup_seconds
        self.warmup_samples = warmup_samples
        self.settings = settings
        self.ffmpeg_path = ffmpeg_path
        self.workers = []
        self.lock = threading.Lock()
        self.running = True

    def worker(self):
        while self.running:
            try:
                url = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue
            if url is STOP:
                self.task_queue.task_done()
                break
            if self.history.is_done(url):
                self.task_queue.task_done()
                continue

            try:
                download_video(url, self.settings, self.ffmpeg_path)
                self.history.mark_done(url)
            except Exception as e:
                print(f"[ERROR] Failed: {url} -> {e}")

            self.task_queue.task_done()

    def start(self):
        for _ in range(self.min_workers):
            t = threading.Thread(target=self.worker)
            t.start()
            self.workers.append(t)

        threading.Thread(target=self._adaptive_scaling, daemon=True).start()

    def stop(self):
        self.running = False
        for _ in self.workers:
            self.task_queue.put(STOP)
        for t in self.workers:
            t.join()

    def _adaptive_scaling(self):
        while self.running:
            time.sleep(self.scale_interval)
            cpu = get_cpu_percent()
            with self.lock:
                if cpu < self.cpu_soft_limit and len(self.workers) < self.max_workers:
                    t = threading.Thread(target=self.worker)
                    t.start()
                    self.workers.append(t)
                elif cpu > self.cpu_hard_limit and len(self.workers) > self.min_workers:
                    self.task_queue.put(STOP)
                  
