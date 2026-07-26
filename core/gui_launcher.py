import socket
import threading
import json
import os
import subprocess
import time

red_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class RedIslandUI:
    """
    Native RedIsland (C# / WPF / SkiaSharp) Dynamic Island UI Launcher for RED Core.
    Launches RedIsland.exe to render Apple-style Dynamic Island notch, animations, widgets,
    music visualizers, and file tray on Windows Desktop.
    """
    def __init__(self, message_callback=None):
        self.host = "127.0.0.1"
        self.port = 8282
        self.client_socket = None
        self.server_socket = None
        self.lock = threading.Lock()
        self.ui_process = None
        self.current_mode = "boot"
        self.message_callback = message_callback
        possible_paths = [
            os.path.join(red_root, "ui", "dynamicwin", "DynamicWin.exe"),
            os.path.join(red_root, "ui", "redisland", "RedIsland.exe"),
            os.path.join(red_root, "ui", "dynamicwin", "RedIsland.exe"),
            os.path.join(red_root, "_internal", "ui", "redisland", "RedIsland.exe"),
            os.path.join(os.path.dirname(red_root), "ui", "redisland", "RedIsland.exe")
        ]
        self.redisland_exe = next((p for p in possible_paths if os.path.exists(p)), possible_paths[0])

    def start(self):
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

        time.sleep(0.5)

        ui_thread = threading.Thread(target=self._spawn_native_ui, daemon=True)
        ui_thread.start()

    def _run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
            print(f"🚩 RED Island Server: Listening on {self.host}:{self.port}...")
            
            while True:
                client, addr = self.server_socket.accept()
                print(f"🚩 RED Island Server: Native RedIsland UI connected from {addr}")
                with self.lock:
                    self.client_socket = client
                
                # Send RED OS initial branding handshake
                self._send_command({
                    "action": "init_branding",
                    "title": "RED OS",
                    "header": "RED OS",
                    "subheader": "Daniel Iwayemi",
                    "brand_name": "RED"
                })
                self._send_command({"action": "set_mode", "mode": self.current_mode})
                self._handle_client(client)
        except Exception as e:
            print(f"🚩 RED Island Server Error: {e}")

    def _handle_client(self, client):
        buffer = ""
        try:
            while True:
                data = client.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            msg = json.loads(line)
                            self._on_message(msg)
                        except Exception as e:
                            print(f"🚩 RED Island Server: JSON decode error: {e} for line: {line}")
        except Exception as e:
            print(f"🚩 RED Island Server: Client disconnected: {e}")
        finally:
            with self.lock:
                if self.client_socket == client:
                    self.client_socket = None
            client.close()

    def _on_message(self, msg):
        action = msg.get("action")
        if action == "user_input":
            text = msg.get("text")
            print(f"🚩 RED Island Server: Received input: {text}")
            if self.message_callback:
                self.message_callback(text)

    def _spawn_native_ui(self):
        """Spawns native C# SkiaSharp RedIsland UI."""
        if os.path.exists(self.redisland_exe):
            ui_dir = os.path.dirname(self.redisland_exe)
            print(f"🚀 RED UI: Launching Native RedIsland UI at {self.redisland_exe}...")
            try:
                logs_dir = os.path.join(red_root, "logs")
                os.makedirs(logs_dir, exist_ok=True)
                log_file = open(os.path.join(logs_dir, "redisland_log.txt"), "a", encoding="utf-8")
                self.ui_process = subprocess.Popen(
                    [self.redisland_exe],
                    cwd=ui_dir,
                    stdout=log_file,
                    stderr=subprocess.STDOUT
                )
                self.ui_process.wait()
                log_file.close()
                print("🚀 RED UI: RedIsland process exited.")
                return
            except Exception as e:
                print(f"🚀 RED UI: Failed to spawn RedIsland.exe: {e}")
        else:
            print(f"⚠️ RED UI: RedIsland.exe not found at {self.redisland_exe}")

    def _send_command(self, cmd):
        with self.lock:
            if self.client_socket:
                try:
                    payload = json.dumps(cmd) + "\n"
                    self.client_socket.sendall(payload.encode("utf-8"))
                except Exception as e:
                    print(f"🚩 RED Island Server: Failed to send command: {e}")
                    self.client_socket = None

    def set_mode(self, mode):
        """Sets the RedIsland mode: boot, idle, active, speaking, vision, spotify."""
        self.current_mode = mode
        self._send_command({"action": "set_mode", "mode": mode})

    def show_reply(self, text):
        """Push RED's reply text into RedIsland's UI panel."""
        self._send_command({"action": "show_reply", "text": text})

    def update_spotify(self, track, artist, art_url=""):
        self._send_command({
            "action": "update_spotify",
            "track": track,
            "artist": artist,
            "art_url": art_url
        })

