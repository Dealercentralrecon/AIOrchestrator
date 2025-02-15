import threading
import time

from .monitor import ResourceMonitor


class ResourcePool:
    def __init__(self):
        self.monitor = ResourceMonitor()
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)

    def start(self):
        self._thread.start()

    def _monitor_loop(self):
        while self._running:
            self.monitor.enforce_limits()
            time.sleep(5)

    def stop(self):
        self._running = False
        self._thread.join()
