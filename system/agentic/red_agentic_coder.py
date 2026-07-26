#!/usr/bin/env python3
"""
RED Core Agentic Coder (Claude Code Competence Module).
Provides RED with autonomous developer capabilities:
- Terminal command execution with output streaming & error recovery
- Precise multi-line file editing & creation
- Codebase grep searching & file viewing
- Git staging, commit, and push automation
- Multi-turn autonomous problem solving loop
"""

import os
import sys
import re
import json
import subprocess
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("RedAgenticCoder")
logging.basicConfig(level=logging.INFO)

class RedAgenticCoder:
    """
    Autonomous Developer Engine for RED Core, matching Claude Code capabilities.
    """
    def __init__(self, workspace_dir: Optional[str] = None):
        self.workspace_dir = workspace_dir or os.getcwd()

    def run_terminal_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Executes a shell command (PowerShell / CMD) safely and returns output.
        """
        target_cwd = cwd or self.workspace_dir
        logger.info(f"Executing Terminal Command: '{command}' in '{target_cwd}'")

        try:
            process = subprocess.run(
                ["powershell.exe", "-Command", command],
                cwd=target_cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": process.returncode == 0,
                "exit_code": process.returncode,
                "stdout": process.stdout.strip(),
                "stderr": process.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds."
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Failed to execute command: {e}"
            }

    def view_file(self, filepath: str, start_line: int = 1, end_line: int = 500) -> Dict[str, Any]:
        """Reads content from target file between start_line and end_line."""
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File '{abs_path}' does not exist."}

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total_lines = len(lines)
            start_idx = max(0, start_line - 1)
            end_idx = min(total_lines, end_line)

            selected_lines = lines[start_idx:end_idx]
            content_with_numbers = "".join(
                f"{i + start_idx + 1}: {line}" for i, line in enumerate(selected_lines)
            )

            return {
                "success": True,
                "filepath": abs_path,
                "total_lines": total_lines,
                "content": content_with_numbers
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to read file: {e}"}

    def replace_in_file(self, filepath: str, target_content: str, replacement_content: str) -> Dict[str, Any]:
        """Replaces exact target_content with replacement_content in target file."""
        abs_path = os.path.abspath(filepath)
        if not os.path.exists(abs_path):
            return {"success": False, "error": f"File '{abs_path}' does not exist."}

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                full_text = f.read()

            if target_content not in full_text:
                return {
                    "success": False,
                    "error": "Target content not found in file. Ensure exact string match including whitespace."
                }

            updated_text = full_text.replace(target_content, replacement_content, 1)

            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(updated_text)

            logger.info(f"Successfully modified file: {abs_path}")
            return {"success": True, "filepath": abs_path, "message": "File updated successfully."}
        except Exception as e:
            return {"success": False, "error": f"Failed to modify file: {e}"}

    def write_to_file(self, filepath: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """Creates or overwrites target file with content."""
        abs_path = os.path.abspath(filepath)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)

        if os.path.exists(abs_path) and not overwrite:
            return {"success": False, "error": f"File '{abs_path}' exists and overwrite is set to False."}

        try:
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Created file: {abs_path}")
            return {"success": True, "filepath": abs_path}
        except Exception as e:
            return {"success": False, "error": f"Failed to write file: {e}"}

    def grep_search(self, query: str, search_path: Optional[str] = None, is_regex: bool = False) -> Dict[str, Any]:
        """Searches files for matching text using python regex."""
        target_dir = search_path or self.workspace_dir
        matches = []
        pattern = re.compile(query if is_regex else re.escape(query), re.IGNORECASE)

        for root, dirs, files in os.walk(target_dir):
            # Exclude build / venv / node_modules / git
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules", "build", "dist", ".venv")]
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        for idx, line in enumerate(f, 1):
                            if pattern.search(line):
                                matches.append({
                                    "file": os.path.relpath(filepath, target_dir),
                                    "line": idx,
                                    "content": line.strip()
                                })
                                if len(matches) >= 100:
                                    break
                except Exception:
                    continue
                if len(matches) >= 100:
                    break

        return {"success": True, "total_matches": len(matches), "matches": matches}

    def git_commit_and_push(self, commit_message: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """Automates git add, commit, and push."""
        target_dir = cwd or self.workspace_dir
        res_add = self.run_terminal_command("git add .", cwd=target_dir)
        if not res_add["success"]:
            return {"success": False, "error": f"Git add failed: {res_add['stderr']}"}

        res_commit = self.run_terminal_command(f'git commit -m "{commit_message}"', cwd=target_dir)
        res_push = self.run_terminal_command("git push", cwd=target_dir)

        return {
            "success": res_push["success"],
            "commit_output": res_commit["stdout"],
            "push_output": res_push["stdout"] or res_push["stderr"]
        }

    def _compact_history(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Claude Code Trajectory Compactor: Summarizes older tool outputs & logs when history grows.
        """
        if len(history) <= 6:
            return history

        compacted = [history[0]]  # Preserve initial task objective
        summary_turns = len(history) - 4
        compacted.append({
            "role": "system",
            "content": f"[Trajectory Compaction: Summarized {summary_turns} previous tool execution turns to save token context.]"
        })
        compacted.extend(history[-4:])  # Keep recent 4 turns
        return compacted

    def solve_task(self, task_prompt: str, max_turns: int = 15) -> Dict[str, Any]:
        """
        Autonomous RED DEV problem solving powered by MIT Hermes + Colibri 744B MoE.
        """
        logger.info(f"[RED DEV] Starting autonomous task via Hermes Agent Engine: {task_prompt}")
        
        try:
            # Ensure agent_engine is in path
            import sys
            import os
            red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            engine_path = os.path.join(red_root, "system", "agent_engine")
            if engine_path not in sys.path:
                sys.path.append(engine_path)
                
            from run_agent import AIAgent
        except ImportError as e:
            logger.error(f"Failed to import Hermes AIAgent: {e}")
            return {"success": False, "error": f"Hermes framework missing or not installed: {e}"}

        try:
            system_prompt = (
                "You are RED DEV, an autonomous software engineering agent powered by a colossal 744B parameter model, "
                "running on the Hermes Agent Framework. "
                "Solve the user's task perfectly using your available tools. "
                "Break tasks down logically, test your edits, and deliver surgical code modifications."
            )
            
            agent = AIAgent(
                model="qwen2.5-coder",
                provider="red_native",
                api_key="red-internal",
                ephemeral_system_prompt=system_prompt
            )
            
            # Use the Hermes agent's chat method to start the autonomous loop
            logger.info("[RED DEV] Handing over control to Hermes...")
            response = agent.chat(task_prompt)
            
            return {
                "success": True, 
                "summary": "Task completed via Hermes Framework.", 
                "result": response
            }
            
        except Exception as e:
            logger.error(f"[RED DEV] Hermes execution failed: {e}")
            return {"success": False, "error": str(e)}

if __name__ == "__main__":
    coder = RedAgenticCoder()
    print("Testing RedAgenticCoder RED DEV Engine...")
    res = coder.solve_task("Verify terminal command execution")
    print(f"Task Output: {res}")
