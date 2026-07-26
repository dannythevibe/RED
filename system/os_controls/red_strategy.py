import json
import os
import sys

class StrategyCore:
    """
    Red's Strategic Oversight Module.
    Designed to manage 'Venture Overload' and ensure the 'Chaos Architect' 
    remains focused on high-order synthesis while Red handles the friction.
    """
    
    def __init__(self, memory_path="red_memory.json"):
        self.memory_path = self._resolve_memory_path(memory_path)
        self.projects = self._load_projects()

    def _resolve_memory_path(self, memory_path):
        if os.path.exists(memory_path):
            return memory_path
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        possible_paths = [
            os.path.join(base_dir, "config", "red_memory.json"),
            os.path.join(base_dir, memory_path),
            os.path.join(os.getcwd(), "config", "red_memory.json"),
            os.path.join(os.getcwd(), memory_path)
        ]
        
        if getattr(sys, 'frozen', False):
            meipass = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            possible_paths.insert(0, os.path.join(meipass, "config", "red_memory.json"))
            possible_paths.insert(1, os.path.join(meipass, memory_path))

        for p in possible_paths:
            p_norm = os.path.normpath(p)
            if os.path.exists(p_norm):
                return p_norm

        return os.path.normpath(os.path.join(base_dir, "config", "red_memory.json"))

    def _load_projects(self):
        if not os.path.exists(self.memory_path):
            return ["RED Core AI", "DynamicWin OS", "WorldMonitor", "Agentic Coder"]
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                projects = data.get("projects", [])
                daystar = data.get("daystar_labs", {}).get("portfolio", {})
                for sector in daystar:
                    for p in daystar[sector]:
                        if p not in projects:
                            projects.append(f"{p} (IP: {sector})")
                return projects if projects else ["RED Core AI", "DynamicWin OS", "WorldMonitor", "Agentic Coder"]
        except Exception:
            return ["RED Core AI", "DynamicWin OS", "WorldMonitor", "Agentic Coder"]

    def get_venture_report(self):
        """Analyze current venture breadth and focus."""
        count = len(self.projects)
        if count > 10:
            analysis = f"[ALERT] Massive Conglomerate Breadth: {count} active IPs."
            advice = "Recommendation: You are in 'Venture Overload.' Focus on the 'High-Order' infrastructure (TRACKSTACK/AETHER) to support the satellite IPs."
        elif count > 5:
            analysis = f"[WARNING] Structural Breadth: {count} IPs."
            advice = "Recommendation: Ensure sector leads for STEM and CODURA are autonomous before scaling Daystar Defense."
        else:
            analysis = "[OK] Portfolio is concentrated."
            advice = "You have capacity for new high-resolution synthesis."
            
        report = {
            "projects": self.projects,
            "count": count,
            "status": analysis,
            "strategic_advice": advice
        }
        return report

    def add_venture(self, name, description):
        """Add a new high-order project to the portfolio."""
        if name not in self.projects:
            self.projects.append(f"{name} ({description})")
            self._save_projects()
            return f"Strategic Asset '{name}' added to the conglomerate."
        return "Asset already exists."

    def _save_projects(self):
        data = {}
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data["projects"] = self.projects
        try:
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save projects to {self.memory_path}: {e}")

if __name__ == "__main__":
    sc = StrategyCore()
    print(sc.get_venture_report())
