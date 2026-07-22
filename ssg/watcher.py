"""File system watcher for development server."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)

WATCH_EXTENSIONS = {".md", ".html", ".css", ".js", ".yaml", ".yml", ".json", ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp"}


class SiteWatcher(FileSystemEventHandler):
    """Watches source directories and triggers rebuilds on changes."""

    def __init__(
        self,
        callback: Callable[[], None],
        debounce_seconds: float = 0.5,
    ) -> None:
        super().__init__()
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def _schedule_rebuild(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._trigger)
            self._timer.daemon = True
            self._timer.start()

    def _trigger(self) -> None:
        logger.info("Change detected, rebuilding...")
        try:
            self.callback()
        except Exception:
            logger.exception("Rebuild failed")

    def on_any_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        src = event.src_path
        if isinstance(src, bytes):
            src = src.decode("utf-8", errors="replace")
        path = Path(src)
        if path.suffix.lower() in WATCH_EXTENSIONS or path.name in ("ssg.yaml",):
            logger.debug("Watch event: %s", event)
            self._schedule_rebuild()


class WatchService:
    """Manages filesystem observer for site development."""

    def __init__(self, watch_paths: list[Path], callback: Callable[[], None]) -> None:
        self.watch_paths = [p.resolve() for p in watch_paths if p.exists()]
        self.callback = callback
        self._observer: Observer | None = None

    def start(self) -> None:
        handler = SiteWatcher(self.callback)
        self._observer = Observer()
        for path in self.watch_paths:
            self._observer.schedule(handler, str(path), recursive=True)
            logger.info("Watching: %s", path)
        self._observer.start()

    def stop(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

    def run_forever(self) -> None:
        """Block until interrupted."""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping watcher...")
        finally:
            self.stop()
# rewrite commit 361
