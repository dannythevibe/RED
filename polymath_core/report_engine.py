import json
import os
from datetime import datetime

class ReportEngine:
    """
    Red's High-Resolution Gap Analysis Engine.
    Generates security reports that map the distance between 
    approximation and the 'correct' state of a system.
    """
    
    def __init__(self, memory_path="red_memory.json"):
        self.memory_path = memory_path

    def generate_gap_report(self, target, findings):
        """
        Synthesize a findings report with 'Chaos Architect' precision.
        findings: list of dicts {'type': 'sqli', 'detail': '...', 'severity': 'high'}
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"🛡️ HIGH-RESOLUTION SECURITY REPORT | {timestamp}\n"
        report += f"🎯 Target: {target}\n"
        report += "="*50 + "\n\n"
        
        if not findings:
            report += "No immediate gaps detected in the current resolution. System appears 'correct.'\n"
        else:
            for i, f in enumerate(findings, 1):
                report += f"[{i}] {f['type'].upper()} — Severity: {f['severity']}\n"
                report += f"   - The Gap: {f['detail']}\n"
                report += f"   - Strategic Advice: Closing this is a requirement for stewardship.\n\n"
        
        report += "="*50 + "\n"
        report += "Status: INCOMPLETE (Awaiting remediation of identified gaps.)\n"
        
        return report

    def save_report(self, report, filename=None):
        if not filename:
            filename = f"knowledge/reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            f.write(report)
        return f"Report archived in {filename}."

if __name__ == "__main__":
    re = ReportEngine()
    test_findings = [{"type": "sqli", "detail": "Unsanitized user input on login.php", "severity": "CRITICAL"}]
    print(re.generate_gap_report("Localhost", test_findings))
