import requests
import json

class ShortcutEngine:
    """
    RED's Shortest-Path Execution Engine.
    Analyzes goals to bypass administrative friction and conventional slow paths.
    """
    
    def __init__(self, model="mistral"):
        self.url = "http://localhost:11434/api/generate"
        self.model = model
        # Pre-coded shortcuts for high-frequency polymath goals
        self.preset_shortcuts = {
            "deploy website": {
                "conventional": "Spin up an AWS EC2 instance, configure Nginx, set up SSL certs via Let's Encrypt manually, configure systemd, deploy code via git.",
                "shortcut": "Run: 'npx vercel' or use Netlify CLI. Single command deployment, auto-SSL, auto-routing, 0 configuration. Takes 30 seconds."
            },
            "get clients": {
                "conventional": "Send cold emails to info@ addresses, apply to Job posts on Upwork/Fiverr with 50 competition proposals, build a complex portfolio website first.",
                "shortcut": "Use lead scrapers (like HIENA) to find companies with broken/outdated UI/UX or missing mobile styling. Send a short, custom loom video directly to the CEO/Founder via LinkedIn showing exactly how to fix it. Close the gap directly."
            },
            "learn song": {
                "conventional": "Spend 2 weeks reading sheet music note-by-note, learning complex scales, and practicing classical structures.",
                "shortcut": "Listen to the chord progression (Roman numeral analysis), identify the key, learn the melody by ear (solfege), and improvise using pentatonic scales. Capture the vibe instantly."
            },
            "secure server": {
                "conventional": "Install massive monitoring dashboards, configure complex firewall rules on multiple layers, install custom active log parsers.",
                "shortcut": "Disable password authentication, change SSH port, turn on public-key-only access, install fail2ban, and close all unused ports using ufw. Done in 3 commands."
            }
        }

    def get_shortcut(self, goal):
        """Analyze a goal and returns the absolute fastest route."""
        goal_lower = goal.lower()
        
        # 1. Check presets
        for key in self.preset_shortcuts:
            if key in goal_lower:
                preset = self.preset_shortcuts[key]
                return self._format_shortcut(goal, preset["conventional"], preset["shortcut"])
        
        # 2. Dynamic generation using Ollama if preset is missing
        return self._generate_dynamic_shortcut(goal)

    def _format_shortcut(self, goal, conventional, shortcut):
        output = (
            f"⚡ RED SHORTCUT ANALYSIS: '{goal.upper()}'\n"
            f"{'='*60}\n"
            f"❌ The Conventional Path (High Friction):\n"
            f"   - {conventional}\n\n"
            f"🔥 The RLC Shortcut (Shortest Path):\n"
            f"   - {shortcut}\n"
            f"{'='*60}\n"
            f"Status: LOCK IN AND EXECUTE."
        )
        return output

    def _generate_dynamic_shortcut(self, goal):
        prompt = (
            f"Analyze this goal: '{goal}'. "
            f"Provide the absolute fastest, easiest, and highest-leverage shortcut to achieve it, bypassing traditional friction. "
            f"Structure your response exactly like this (directly return the text, do not write markdown blocks or system preambles):\n\n"
            f"❌ The Conventional Path (High Friction):\n"
            f"[Explain the slow way in 1 sentence]\n\n"
            f"🔥 The RLC Shortcut (Shortest Path):\n"
            f"[Explain the out-of-the-box shortcut in 1-2 sentences]"
        )
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            if response.status_code == 200:
                raw_reply = response.json().get("response", "").strip()
                return (
                    f"⚡ RED SHORTCUT ANALYSIS: '{goal.upper()}'\n"
                    f"{'='*60}\n"
                    f"{raw_reply}\n"
                    f"{'='*60}\n"
                    f"Status: LOCK IN AND EXECUTE."
                )
        except Exception:
            pass
            
        # Fallback if Ollama is offline
        return self._format_shortcut(
            goal,
            "Long-winded setup and manual documentation lookup.",
            "Deconstruct the goal into the single highest-value action and automate or bypass the setup entirely."
        )

if __name__ == "__main__":
    se = ShortcutEngine()
    print(se.get_shortcut("deploy website"))
