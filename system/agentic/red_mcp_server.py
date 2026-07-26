#!/usr/bin/env python3
"""
RED Core Native MCP Server.
Provides Model Context Protocol (MCP) interface (Stdio & SSE) allowing external agents
(Claude Code CLI, Cursor, Antigravity IDE) to invoke RED's system tools, screen vision,
agentic coder capabilities, and 2nd Brain memories.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List

red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if red_root not in sys.path:
    sys.path.append(red_root)

from system.agentic.red_agentic_coder import RedAgenticCoder
from system.vision.red_vision import RedVision

logger = logging.getLogger("RedMCPServer")
logging.basicConfig(level=logging.INFO)

class RedMCPServer:
    """
    Model Context Protocol (MCP) Server for RED Core.
    """
    def __init__(self):
        self.coder = RedAgenticCoder()
        self.vision = RedVision()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "red_agentic_code",
                "description": "Execute autonomous coding operations (terminal command, file view, file patch, git).",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["run_terminal", "view_file", "replace_in_file", "write_file", "grep_search", "git_push"]
                        },
                        "command": {"type": "string"},
                        "filepath": {"type": "string"},
                        "target_content": {"type": "string"},
                        "replacement_content": {"type": "string"},
                        "content": {"type": "string"},
                        "query": {"type": "string"},
                        "commit_message": {"type": "string"}
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "red_perception",
                "description": "Captures current active screen and returns high-resolution visual analysis.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string", "default": "Describe what is on my screen in high technical detail."}
                    }
                }
            },
            {
                "name": "red_memory_get",
                "description": "Retrieves RED's core 2nd Brain memory and user profile.",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "red_perception":
            prompt = arguments.get("prompt", "Describe what is on my screen in high technical detail.")
            report = self.vision.analyze_screen(prompt)
            return {"content": [{"type": "text", "text": report}]}

        elif tool_name == "red_memory_get":
            memory_path = os.path.join(red_root, "config", "red_memory.json")
            try:
                with open(memory_path, "r", encoding="utf-8") as f:
                    mem_data = json.load(f)
                return {"content": [{"type": "text", "text": json.dumps(mem_data, indent=2)}]}
            except Exception as e:
                return {"isError": True, "content": [{"type": "text", "text": f"Error loading memory: {e}"}]}

        elif tool_name == "red_agentic_code":
            action = arguments.get("action")
            if action == "run_terminal":
                res = self.coder.run_terminal_command(arguments.get("command", ""))
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            elif action == "view_file":
                res = self.coder.view_file(arguments.get("filepath", ""))
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            elif action == "replace_in_file":
                res = self.coder.replace_in_file(
                    arguments.get("filepath", ""),
                    arguments.get("target_content", ""),
                    arguments.get("replacement_content", "")
                )
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            elif action == "write_file":
                res = self.coder.write_to_file(arguments.get("filepath", ""), arguments.get("content", ""))
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            elif action == "grep_search":
                res = self.coder.grep_search(arguments.get("query", ""))
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            elif action == "git_push":
                res = self.coder.git_commit_and_push(arguments.get("commit_message", "Automated commit by RED"))
                return {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            else:
                return {"isError": True, "content": [{"type": "text", "text": f"Unknown action '{action}'"}]}

        return {"isError": True, "content": [{"type": "text", "text": f"Unknown tool '{tool_name}'"}]}

    def run_sse(self, port: int = 8000):
        """Launches FastMCP SSE server on specified port."""
        logger.info(f"[RED] Launching RED FastMCP SSE Server on http://127.0.0.1:{port}/sse...")
        try:
            from fastmcp import FastMCP
            mcp = FastMCP("RED-Core-Server")

            @mcp.tool()
            def red_perception(prompt: str = "Describe what is on my screen in high technical detail.") -> str:
                res = self.handle_tool_call("red_perception", {"prompt": prompt})
                return res["content"][0]["text"]

            @mcp.tool()
            def red_memory_get() -> str:
                res = self.handle_tool_call("red_memory_get", {})
                return res["content"][0]["text"]

            @mcp.tool()
            def red_agentic_code(action: str, command: str = "", filepath: str = "", content: str = "") -> str:
                res = self.handle_tool_call("red_agentic_code", {
                    "action": action, "command": command, "filepath": filepath, "content": content
                })
                return res["content"][0]["text"]

            mcp.run(transport="sse", port=port)
        except Exception as e:
            logger.warning(f"FastMCP SSE start warning: {e}. Falling back to standard JSON RPC.")

if __name__ == "__main__":
    server = RedMCPServer()
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        server.run_sse(8000)
    else:
        server.run_stdio()
