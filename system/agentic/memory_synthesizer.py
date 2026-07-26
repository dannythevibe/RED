import json
import os
import re

_MAX_SESSION_NOTES = 50  # cap to prevent unbounded growth

class MemorySynthesizer:
    """
    Red's Autonomous Memory Extraction Engine.
    Analyzes user input for new facts, project updates, and strategic
    markers to maintain a 'Dynamic Reflection.'
    """

    def __init__(self, memory_path="red_memory.json"):
        self.memory_path = memory_path

    def _load_memory(self):
        try:
            with open(self.memory_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            print("MemorySynthesizer: Memory file corrupted. Using empty state.")
            return {}

    def _save_memory(self, data):
        try:
            with open(self.memory_path, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"MemorySynthesizer: Failed to save memory — {e}")

    def synthesize_interaction(self, user_input):
        """
        Extract key updates from a single interaction.
        Pattern-based for prototype (LLM-based in full version).
        """
        memory = self._load_memory()
        updated = False

        # 1. Daystar Labs Portfolio Detection
        if any(kw in user_input.lower() for kw in ("daystar", "nebula", "aether")):
            if "session_notes" not in memory:
                memory["session_notes"] = []

            note = f"Update detected: {user_input[:100]}"
            # Deduplicate — don't append the exact same note twice
            if note not in memory["session_notes"]:
                memory["session_notes"].append(note)
                # Keep only the most recent N notes
                if len(memory["session_notes"]) > _MAX_SESSION_NOTES:
                    memory["session_notes"] = memory["session_notes"][-_MAX_SESSION_NOTES:]
                updated = True

        # 2. Personal Fact Detection (e.g. "I'm 19 now")
        age_match = re.search(r"i'm (\d+) now", user_input.lower())
        if age_match:
            memory["age"] = int(age_match.group(1))
            updated = True

        if updated:
            self._save_memory(memory)
            return "Cognitive Update: Your memory lattice has been synchronized."
        return None

if __name__ == "__main__":
    ms = MemorySynthesizer()
    print(ms.synthesize_interaction("I'm 19 now and we need to scale Nebula."))
