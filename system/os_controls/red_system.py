import os
import subprocess
import webbrowser
import keyboard
import time
import urllib.parse
try:
    import pyautogui
except ImportError:
    pyautogui = None

class SystemController:
    """
    Red's System Core.
    Handles direct interaction with the Windows Operating System.
    """

    @staticmethod
    def power_shutdown():
        """Shut down the PC immediately."""
        print("Red: Initiating system shutdown...")
        try:
            result = subprocess.run(["shutdown", "/s", "/t", "5"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Shutdown failed: {result.stderr.strip()}")
            return True
        except Exception as e:
            print(f"Red: Shutdown error: {e}")
            raise

    @staticmethod
    def power_restart():
        """Restart the PC."""
        print("Red: Initiating system restart...")
        try:
            result = subprocess.run(["shutdown", "/r", "/t", "5"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Restart failed: {result.stderr.strip()}")
            return True
        except Exception as e:
            print(f"Red: Restart error: {e}")
            raise

    @staticmethod
    def power_sleep():
        """Put the PC to sleep."""
        print("Red: Initiating sleep mode...")
        try:
            result = subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Sleep command failed")
            return True
        except Exception as e:
            print(f"Red: Sleep error: {e}")
            raise

    @staticmethod
    def is_url(target):
        target_lower = target.lower()
        if target_lower.startswith("http://") or target_lower.startswith("https://") or target_lower.startswith("www."):
            return True
        if "." in target and any(target_lower.endswith(ext) or (ext + "/") in target_lower for ext in [".com", ".org", ".net", ".io", ".co"]):
            return True
        if target_lower in ["youtube", "google", "twitter", "facebook", "github", "linkedin", "reddit"]:
            return True
        return False

    @staticmethod
    def format_url(target):
        if target.lower() in ["youtube", "google", "twitter", "facebook", "github", "linkedin", "reddit"]:
            return f"https://www.{target.lower()}.com"
        if not target.startswith("http"):
            return "https://" + target
        return target

    @staticmethod
    def open_app(app_name):
        """
        Universal Application Opener. Tries multiple methods to execute software or open web pages.
        """
        print(f"Red: Attempting universal open for '{app_name}'...")
        target = app_name.strip()
        
        if SystemController.is_url(target):
            url = SystemController.format_url(target)
            print(f"Red: Detected URL. Opening in browser: {url}")
            webbrowser.open(url)
            return True

        # Method 1: os.startfile
        try:
            os.startfile(target)
            return True
        except Exception as e:
            print(f"Red: os.startfile failed for {target}: {e}")
            
        # Method 2: Direct execution via PATH
        try:
            subprocess.Popen([target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            print(f"Red: Direct Popen failed for {target}: {e}")

        return False

    @staticmethod
    def type_text(text, delay=0.05):
        """
        Typing out text as if the user were typing it.
        """
        print(f"Red: Typing: '{text[:20]}...'")
        for char in text:
            keyboard.write(char)
            time.sleep(delay)
            
    @staticmethod
    def execute_command(command):
        """Runs a shell command and returns output."""
        print(f"Red: Executing command: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout
            if result.stderr:
                output += f"\n[Errors]:\n{result.stderr}"
            return output if output.strip() else "[Command executed successfully with no output]"
        except subprocess.TimeoutExpired:
            return "[Error: Command timed out after 30 seconds]"
        except Exception as e:
            raise Exception(f"Command failed: {str(e)}")

    @staticmethod
    def mouse_move(x, y):
        if not pyautogui:
            raise Exception("pyautogui is not installed. Run 'pip install pyautogui' first.")
        pyautogui.moveTo(int(x), int(y), duration=0.25)
        
    @staticmethod
    def mouse_click(button="left", clicks=1):
        if not pyautogui:
            raise Exception("pyautogui is not installed. Run 'pip install pyautogui' first.")
        pyautogui.click(button=button, clicks=int(clicks))
        
    @staticmethod
    def mouse_scroll(amount):
        if not pyautogui:
            raise Exception("pyautogui is not installed. Run 'pip install pyautogui' first.")
        pyautogui.scroll(int(amount))

    @staticmethod
    def press_key(key):
        if not pyautogui:
            keyboard.send(key)
            return
        pyautogui.press(key)

if __name__ == "__main__":
    sc = SystemController()
    print("System Controller Module Ready.")
