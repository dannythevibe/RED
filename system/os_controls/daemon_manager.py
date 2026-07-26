"""
RED Central Daemon Manager.
Orchestrates background processes (OSIRIS, future services) as child processes
that are bound to red.exe's lifecycle. If a child crashes, it is automatically
restarted without taking down the parent system.
"""

import os
import sys
import subprocess
import threading
import logging
import time

logger = logging.getLogger(__name__)

red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ManagedDaemon:
    """Tracks a single managed child process."""
    def __init__(self, name, command, cwd, max_restarts=5, restart_delay=3.0):
        self.name = name
        self.command = command
        self.cwd = cwd
        self.max_restarts = max_restarts
        self.restart_delay = restart_delay
        self.process = None
        self.restarts = 0
        self.running = False
        self._thread = None

    def start(self):
        """Launch the daemon in a background thread."""
        self.running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name=f"daemon-{self.name}")
        self._thread.start()
        logger.info(f"[DaemonManager] Started daemon: {self.name}")

    def _run_loop(self):
        """Main loop: launch process, watch for crashes, auto-restart."""
        while self.running and self.restarts <= self.max_restarts:
            try:
                logger.info(f"[DaemonManager] Launching {self.name}: {self.command}")
                self.process = subprocess.Popen(
                    self.command,
                    cwd=self.cwd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )
                # Block until the process exits
                self.process.wait()
                exit_code = self.process.returncode

                if not self.running:
                    # We were asked to stop, don't restart
                    break

                logger.warning(f"[DaemonManager] {self.name} exited with code {exit_code}. Restarting in {self.restart_delay}s...")
                self.restarts += 1
                time.sleep(self.restart_delay)

            except Exception as e:
                logger.error(f"[DaemonManager] {self.name} failed to launch: {e}")
                self.restarts += 1
                time.sleep(self.restart_delay)

        if self.restarts > self.max_restarts:
            logger.error(f"[DaemonManager] {self.name} exceeded max restarts ({self.max_restarts}). Giving up.")

    def stop(self):
        """Gracefully stop the daemon."""
        self.running = False
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.warning(f"[DaemonManager] Failed to stop {self.name}: {e}")
        logger.info(f"[DaemonManager] Stopped daemon: {self.name}")


class DaemonManager:
    """Central orchestrator for all RED background daemons."""
    def __init__(self):
        self.daemons = {}

    def register(self, name, command, cwd, max_restarts=5, restart_delay=3.0):
        """Register a new daemon."""
        daemon = ManagedDaemon(name, command, cwd, max_restarts, restart_delay)
        self.daemons[name] = daemon
        return daemon

    def start_all(self):
        """Boot all registered daemons."""
        for name, daemon in self.daemons.items():
            daemon.start()

    def stop_all(self):
        """Gracefully stop all daemons."""
        for name, daemon in self.daemons.items():
            daemon.stop()

    def status(self):
        """Return status of all daemons."""
        report = {}
        for name, daemon in self.daemons.items():
            alive = daemon.process and daemon.process.poll() is None
            report[name] = {
                "alive": alive,
                "restarts": daemon.restarts,
                "pid": daemon.process.pid if daemon.process else None
            }
        return report


def create_default_manager():
    """Factory: creates a DaemonManager pre-loaded with RED's standard daemons."""
    manager = DaemonManager()

    # OSIRIS World Monitor (Next.js)
    osiris_dir = os.path.join(red_root, "ui", "osiris")
    if os.path.isdir(osiris_dir):
        manager.register(
            name="osiris",
            command="npm run dev",
            cwd=osiris_dir,
            max_restarts=3,
            restart_delay=5.0
        )

    return manager
