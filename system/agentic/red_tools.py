#!/usr/bin/env python3
"""
RED Native Subsystem Tools Module.
Bridges RED's custom modules (OS controls, screen perception, RAG vector database,
and mentoring academy) as native tools in the Hermes Agent framework.
"""

import os
import sys
import json
import logging

# Ensure agent_engine path is present so we can import registry
red_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
engine_path = os.path.join(red_root, "system", "agent_engine")
if engine_path not in sys.path:
    sys.path.append(engine_path)
if red_root not in sys.path:
    sys.path.append(red_root)

from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

# The registry bridge to hold RED's initialized singleton instances.
# Populated by red.py at startup.
_red_bridge = {}

def get_red_bridge():
    return _red_bridge

# =============================================================================
# Tool Handlers
# =============================================================================

def red_open_app_tool(app_name: str) -> str:
    """Open a Windows application or file."""
    sys_ctrl = _red_bridge.get("sys_ctrl")
    if not sys_ctrl:
        return tool_error("SystemController not initialized in bridge.")
    try:
        success = sys_ctrl.open_app(app_name)
        return json.dumps({"success": success, "message": f"App '{app_name}' open request sent."})
    except Exception as e:
        return tool_error(f"Failed to open app '{app_name}': {e}")

def red_power_control_tool(action: str) -> str:
    """Execute Windows OS power operations."""
    sys_ctrl = _red_bridge.get("sys_ctrl")
    if not sys_ctrl:
        return tool_error("SystemController not initialized in bridge.")
    try:
        act = action.lower().strip()
        if "shutdown" in act:
            sys_ctrl.power_shutdown()
            return json.dumps({"success": True, "message": "System shutdown initiated."})
        elif "restart" in act or "reboot" in act:
            sys_ctrl.power_restart()
            return json.dumps({"success": True, "message": "System restart initiated."})
        elif "sleep" in act:
            sys_ctrl.power_sleep()
            return json.dumps({"success": True, "message": "System sleep mode initiated."})
        else:
            return tool_error(f"Unrecognized power action '{action}'. Supported: shutdown, restart, sleep.")
    except Exception as e:
        return tool_error(f"Failed to execute power action '{action}': {e}")

def red_type_text_tool(text: str, delay: float = 0.05) -> str:
    """Simulate OS keyboard typing."""
    sys_ctrl = _red_bridge.get("sys_ctrl")
    if not sys_ctrl:
        return tool_error("SystemController not initialized in bridge.")
    try:
        sys_ctrl.type_text(text, delay)
        return json.dumps({"success": True, "message": f"Typed {len(text)} characters."})
    except Exception as e:
        return tool_error(f"Failed to type text: {e}")

def red_execute_command_tool(command: str) -> str:
    """Execute a shell command on the host OS."""
    sys_ctrl = _red_bridge.get("sys_ctrl")
    if not sys_ctrl:
        return tool_error("SystemController not initialized in bridge.")
    try:
        output = sys_ctrl.execute_command(command)
        return json.dumps({"success": True, "output": output})
    except Exception as e:
        return tool_error(f"Failed to execute command '{command}': {e}")

def red_mouse_control_tool(action: str, x: int = 0, y: int = 0, button: str = "left", clicks: int = 1, amount: int = 0) -> str:
    """Control the mouse."""
    sys_ctrl = _red_bridge.get("sys_ctrl")
    if not sys_ctrl:
        return tool_error("SystemController not initialized in bridge.")
    try:
        if action == "move":
            sys_ctrl.mouse_move(x, y)
            return json.dumps({"success": True, "message": f"Mouse moved to ({x}, {y})."})
        elif action == "click":
            sys_ctrl.mouse_click(button, clicks)
            return json.dumps({"success": True, "message": f"Mouse clicked {button} {clicks} times."})
        elif action == "scroll":
            sys_ctrl.mouse_scroll(amount)
            return json.dumps({"success": True, "message": f"Mouse scrolled by {amount}."})
        else:
            return tool_error(f"Unknown mouse action: {action}")
    except Exception as e:
        return tool_error(f"Failed to perform mouse action '{action}': {e}")

def red_keyboard_control_tool(key: str) -> str:
    """Press a specific keyboard key (e.g., 'enter', 'tab', 'win')."""
    sys_ctrl = _red_bridge.get("sys_ctrl")
    if not sys_ctrl:
        return tool_error("SystemController not initialized in bridge.")
    try:
        sys_ctrl.press_key(key)
        return json.dumps({"success": True, "message": f"Pressed key '{key}'."})
    except Exception as e:
        return tool_error(f"Failed to press key '{key}': {e}")

def red_perception_tool() -> str:
    """Analyze current screen content via vision."""
    vision_engine = _red_bridge.get("vision_engine")
    if not vision_engine:
        return tool_error("RedVision not initialized in bridge.")
    try:
        report = vision_engine.analyze_screen()
        return json.dumps({"success": True, "report": report})
    except Exception as e:
        return tool_error(f"Failed to analyze screen: {e}")

def red_knowledge_search_tool(query: str, top_k: int = 3) -> str:
    """Perform semantic search across RED's offline RAG database."""
    knowledge_base = _red_bridge.get("knowledge_base")
    if not knowledge_base:
        return tool_error("RedRAG not initialized in bridge.")
    try:
        results = knowledge_base.query(query, top_k=top_k)
        return json.dumps({"success": True, "results": results})
    except Exception as e:
        return tool_error(f"Failed to query knowledge base: {e}")

def red_knowledge_ingest_tool(title: str, text: str) -> str:
    """Ingest document into local compressed RAG database."""
    knowledge_base = _red_bridge.get("knowledge_base")
    if not knowledge_base:
        return tool_error("RedRAG not initialized in bridge.")
    try:
        msg = knowledge_base.ingest_document(title, text)
        return json.dumps({"success": True, "message": msg})
    except Exception as e:
        return tool_error(f"Failed to ingest document: {e}")

def red_academy_get_lesson_tool(topic: str) -> str:
    """Retrieve Polymath curriculum lessons."""
    academy = _red_bridge.get("academy")
    if not academy:
        return tool_error("PolymathAcademy not initialized in bridge.")
    try:
        lesson = academy.get_lesson(topic)
        return json.dumps({"success": True, "lesson": lesson})
    except Exception as e:
        return tool_error(f"Failed to retrieve lesson: {e}")

def red_academy_get_guide_tool(tool_name: str) -> str:
    """Resolve step-by-step handbook guides."""
    academy = _red_bridge.get("academy")
    if not academy:
        return tool_error("PolymathAcademy not initialized in bridge.")
    try:
        guide = academy.get_guide(tool_name)
        return json.dumps({"success": True, "guide": guide})
    except Exception as e:
        return tool_error(f"Failed to retrieve guide: {e}")

def red_get_venture_report_tool() -> str:
    """Retrieve Daystar portfolio venture reports."""
    strat_core = _red_bridge.get("strat_core")
    if not strat_core:
        return tool_error("StrategyCore not initialized in bridge.")
    try:
        report = strat_core.get_venture_report()
        return json.dumps({"success": True, "report": report})
    except Exception as e:
        return tool_error(f"Failed to retrieve venture report: {e}")

def red_add_venture_tool(name: str, description: str) -> str:
    """Add a new venture to Daystar Labs portfolio."""
    strat_core = _red_bridge.get("strat_core")
    if not strat_core:
        return tool_error("StrategyCore not initialized in bridge.")
    try:
        msg = strat_core.add_venture(name, description)
        return json.dumps({"success": True, "message": msg})
    except Exception as e:
        return tool_error(f"Failed to add strategic asset: {e}")

# =============================================================================
# Tool Schemas & Registrations
# =============================================================================

RED_OPEN_APP_SCHEMA = {
    "name": "red_open_app",
    "description": "Open a Windows application or file (e.g. 'notepad', 'chrome', 'spotify') on the host system.",
    "parameters": {
        "type": "object",
        "properties": {
            "app_name": {
                "type": "string",
                "description": "Name or executable name of the app to open (e.g., 'notepad', 'chrome', 'spotify').",
            }
        },
        "required": ["app_name"],
    },
}

RED_POWER_CONTROL_SCHEMA = {
    "name": "red_power_control",
    "description": "Perform power state actions on the host OS (shutdown immediately, restart/reboot, or sleep).",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["shutdown", "restart", "sleep"],
                "description": "The power state action to execute.",
            }
        },
        "required": ["action"],
    },
}

RED_TYPE_TEXT_SCHEMA = {
    "name": "red_type_text",
    "description": "Simulate typing text characters on the host OS keyboard.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The exact text string to type out.",
            },
            "delay": {
                "type": "number",
                "description": "Delay in seconds between keystrokes. Default is 0.05.",
            }
        },
        "required": ["text"],
    },
}

RED_EXECUTE_COMMAND_SCHEMA = {
    "name": "red_execute_command",
    "description": "Execute an arbitrary shell command (like Command Prompt) and return its output.",
    "parameters": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The exact shell command to execute.",
            }
        },
        "required": ["command"],
    },
}

RED_MOUSE_CONTROL_SCHEMA = {
    "name": "red_mouse_control",
    "description": "Control the mouse cursor on the host OS for DOM manipulation or desktop UI interaction.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["move", "click", "scroll"],
                "description": "The mouse action to perform.",
            },
            "x": {"type": "integer", "description": "X coordinate for 'move' action."},
            "y": {"type": "integer", "description": "Y coordinate for 'move' action."},
            "button": {"type": "string", "enum": ["left", "right", "middle"], "description": "Button for 'click' action."},
            "clicks": {"type": "integer", "description": "Number of clicks for 'click' action."},
            "amount": {"type": "integer", "description": "Scroll amount for 'scroll' action."}
        },
        "required": ["action"],
    },
}

RED_KEYBOARD_CONTROL_SCHEMA = {
    "name": "red_keyboard_control",
    "description": "Press a specific keyboard key (e.g., 'enter', 'tab', 'win', 'esc').",
    "parameters": {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "The key to press.",
            }
        },
        "required": ["key"],
    },
}

RED_PERCEPTION_SCHEMA = {
    "name": "red_perception",
    "description": "Capture a screenshot and perform high-resolution vision perception analysis on the host system.",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

RED_KNOWLEDGE_SEARCH_SCHEMA = {
    "name": "red_knowledge_search",
    "description": "Perform semantic search across RED's offline hyper-compressed vector memory index.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to look up semantically in local vector storage.",
            },
            "top_k": {
                "type": "integer",
                "description": "Number of top results to retrieve. Default is 3.",
            }
        },
        "required": ["query"],
    },
}

RED_KNOWLEDGE_INGEST_SCHEMA = {
    "name": "red_knowledge_ingest",
    "description": "Ingest a new document/text block into RED's local vector index for long-term semantic retrieval.",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "The title or subject label of the document.",
            },
            "text": {
                "type": "string",
                "description": "The full text content to chunk, embed, and index.",
            }
        },
        "required": ["title", "text"],
    },
}

RED_ACADEMY_GET_LESSON_SCHEMA = {
    "name": "red_academy_get_lesson",
    "description": "Retrieve curriculum mentorship lessons across cybersecurity, rhythm/acoustics, UI design, and fintech rails.",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The curriculum topic name (e.g., 'recon', 'rhythm', 'design', 'rails').",
            }
        },
        "required": ["topic"],
    },
}

RED_ACADEMY_GET_GUIDE_SCHEMA = {
    "name": "red_academy_get_guide",
    "description": "Resolve step-by-step handbook guides (e.g. gobuster, music_improv, glass_css).",
    "parameters": {
        "type": "object",
        "properties": {
            "tool_name": {
                "type": "string",
                "description": "The handbook guide identifier (e.g. 'gobuster', 'music_improv', 'glass_css').",
            }
        },
        "required": ["tool_name"],
    },
}

RED_GET_VENTURE_REPORT_SCHEMA = {
    "name": "red_get_venture_report",
    "description": "Analyze and print reports about Daniel's active conglomerate ventures and Daystar Labs portfolio.",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

RED_ADD_VENTURE_SCHEMA = {
    "name": "red_add_venture",
    "description": "Add a new strategic project/IP asset to the Daystar Labs venture portfolio.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the venture/IP.",
            },
            "description": {
                "type": "string",
                "description": "Brief description of the venture's target domain or focus.",
            }
        },
        "required": ["name", "description"],
    },
}

# Register all tools with the central registry
registry.register(
    name="red_open_app",
    toolset="red_core",
    schema=RED_OPEN_APP_SCHEMA,
    handler=lambda args, **kw: red_open_app_tool(app_name=args.get("app_name", "")),
    emoji="[APP]",
)

registry.register(
    name="red_power_control",
    toolset="red_core",
    schema=RED_POWER_CONTROL_SCHEMA,
    handler=lambda args, **kw: red_power_control_tool(action=args.get("action", "")),
    emoji="[POWER]",
)

registry.register(
    name="red_type_text",
    toolset="red_core",
    schema=RED_TYPE_TEXT_SCHEMA,
    handler=lambda args, **kw: red_type_text_tool(text=args.get("text", ""), delay=args.get("delay", 0.05)),
    emoji="[TYPE]",
)

registry.register(
    name="red_execute_command",
    toolset="red_core",
    schema=RED_EXECUTE_COMMAND_SCHEMA,
    handler=lambda args, **kw: red_execute_command_tool(command=args.get("command", "")),
    emoji="[CMD]",
)

registry.register(
    name="red_mouse_control",
    toolset="red_core",
    schema=RED_MOUSE_CONTROL_SCHEMA,
    handler=lambda args, **kw: red_mouse_control_tool(
        action=args.get("action", ""),
        x=args.get("x", 0),
        y=args.get("y", 0),
        button=args.get("button", "left"),
        clicks=args.get("clicks", 1),
        amount=args.get("amount", 0)
    ),
    emoji="[MOUSE]",
)

registry.register(
    name="red_keyboard_control",
    toolset="red_core",
    schema=RED_KEYBOARD_CONTROL_SCHEMA,
    handler=lambda args, **kw: red_keyboard_control_tool(key=args.get("key", "")),
    emoji="[KEY]",
)

registry.register(
    name="red_perception",
    toolset="red_core",
    schema=RED_PERCEPTION_SCHEMA,
    handler=lambda args, **kw: red_perception_tool(),
    emoji="[VISION]",
)

registry.register(
    name="red_knowledge_search",
    toolset="red_core",
    schema=RED_KNOWLEDGE_SEARCH_SCHEMA,
    handler=lambda args, **kw: red_knowledge_search_tool(query=args.get("query", ""), top_k=args.get("top_k", 3)),
    emoji="[SEARCH]",
)

registry.register(
    name="red_knowledge_ingest",
    toolset="red_core",
    schema=RED_KNOWLEDGE_INGEST_SCHEMA,
    handler=lambda args, **kw: red_knowledge_ingest_tool(title=args.get("title", ""), text=args.get("text", "")),
    emoji="[INGEST]",
)

registry.register(
    name="red_academy_get_lesson",
    toolset="red_core",
    schema=RED_ACADEMY_GET_LESSON_SCHEMA,
    handler=lambda args, **kw: red_academy_get_lesson_tool(topic=args.get("topic", "")),
    emoji="[ACADEMY]",
)

registry.register(
    name="red_academy_get_guide",
    toolset="red_core",
    schema=RED_ACADEMY_GET_GUIDE_SCHEMA,
    handler=lambda args, **kw: red_academy_get_guide_tool(tool_name=args.get("tool_name", "")),
    emoji="[GUIDE]",
)

import httpx
import xml.etree.ElementTree as ET
import asyncio
import re
import webbrowser

SEED_NEWS_FEEDS = [
    'https://feeds.bbci.co.uk/news/world/rss.xml',
    'https://www.cnbc.com/id/100727362/device/rss/rss.html',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.aljazeera.com/xml/rss/all.xml'
]

SEED_FINANCE_FEEDS = [
    'https://www.cnbc.com/id/10000664/device/rss/rss.html',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://feeds.marketwatch.com/marketwatch/topstories/',
    'https://rss.nytimes.com/services/xml/rss/nyt/Business.xml'
]

async def _fetch_and_parse_feed(client, url):
    try:
        response = await client.get(url, headers={'User-Agent': 'RED-Core-AI/1.0'}, timeout=5.0)
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        source_name = url.split('.')[1].upper() if '.' in url else "NEWS"
        feed_items = []
        for item in root.findall(".//item")[:5]:
            title = item.findtext("title")
            description = item.findtext("description")
            link = item.findtext("link")
            if description:
                description = re.sub('<[^<]+?>', '', description).strip()
            feed_items.append({
                "source": source_name,
                "title": title,
                "summary": description[:200] + "..." if description else "",
                "link": link
            })
        return feed_items
    except Exception:
        return []

def red_get_world_news_tool() -> str:
    """Scrape live international headlines from global news networks in parallel."""
    async def _gather_all():
        async with httpx.AsyncClient(follow_redirects=True, timeout=8.0) as client:
            tasks = [_fetch_and_parse_feed(client, url) for url in SEED_NEWS_FEEDS]
            results = await asyncio.gather(*tasks)
            return [item for sub in results for item in sub]
    try:
        articles = asyncio.run(_gather_all())
        if not articles:
            return json.dumps({"success": False, "message": "Live news feed grid unreachable."})
        report = ["### GLOBAL LIVE INTELLIGENCE BRIEFING\n"]
        for entry in articles[:10]:
            report.append(f"**[{entry['source']}]** {entry['title']}")
            report.append(f"{entry['summary']}\n")
        return json.dumps({"success": True, "briefing": "\n".join(report)})
    except Exception as e:
        return tool_error(f"Failed to fetch live news: {e}")

def red_get_world_finance_news_tool() -> str:
    """Scrape live global market and economy headlines in parallel."""
    async def _gather_all():
        async with httpx.AsyncClient(follow_redirects=True, timeout=8.0) as client:
            tasks = [_fetch_and_parse_feed(client, url) for url in SEED_FINANCE_FEEDS]
            results = await asyncio.gather(*tasks)
            return [item for sub in results for item in sub]
    try:
        articles = asyncio.run(_gather_all())
        if not articles:
            return json.dumps({"success": False, "message": "Live financial feed grid unreachable."})
        report = ["### GLOBAL FINANCE LIVE BRIEFING\n"]
        for entry in articles[:10]:
            report.append(f"**[{entry['source']}]** {entry['title']}")
            report.append(f"{entry['summary']}\n")
        return json.dumps({"success": True, "briefing": "\n".join(report)})
    except Exception as e:
        return tool_error(f"Failed to fetch financial news: {e}")

_worldmonitor_process = None

def start_local_worldmonitor(variant: str = "full") -> str:
    global _worldmonitor_process
    import subprocess
    import socket
    import time
    
    # Check if already running
    if _worldmonitor_process is not None:
        if _worldmonitor_process.poll() is None:
            return "http://localhost:3000"
            
    wm_path = os.path.join(red_root, "ui", "osiris")
    if not os.path.exists(wm_path):
        return ""
        
    # Check node_modules
    node_modules = os.path.join(wm_path, "node_modules")
    if not os.path.exists(node_modules):
        try:
            print("[RED] Installing local OSIRIS dashboard dependencies...")
            subprocess.run("npm install", shell=True, cwd=wm_path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[RED Warning] npm install failed: {e}")
            
    # Start Next.js dev server
    try:
        cmd = "npm run dev"
        print(f"[RED] Launching local OSIRIS dashboard...")
        _worldmonitor_process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=wm_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for port 3000 to open
        for _ in range(30):
            time.sleep(0.5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(("127.0.0.1", 3000))
                s.close()
                return "http://localhost:3000"
            except Exception:
                pass
        return "http://localhost:3000"
    except Exception as e:
        print(f"[RED Warning] Failed to launch OSIRIS server: {e}")
        return ""

def red_open_world_monitor_tool() -> str:
    """Open the live World Monitor interactive map dashboard in browser."""
    try:
        local_url = start_local_worldmonitor("full")
        if local_url:
            webbrowser.open(local_url)
            return json.dumps({"success": True, "message": f"Opened local OSIRIS dashboard at {local_url}."})
        else:
            webbrowser.open("https://osirisai.live")
            return json.dumps({"success": True, "message": "Opened online OSIRIS dashboard."})
    except Exception as e:
        return tool_error(f"Failed to launch OSIRIS World Monitor: {e}")

def red_open_finance_world_monitor_tool() -> str:
    """Open the live Global Finance Monitor dashboard in browser."""
    try:
        local_url = start_local_worldmonitor("finance")
        if local_url:
            webbrowser.open(local_url)
            return json.dumps({"success": True, "message": f"Opened local OSIRIS dashboard at {local_url}."})
        else:
            webbrowser.open("https://osirisai.live")
            return json.dumps({"success": True, "message": "Opened online OSIRIS dashboard."})
    except Exception as e:
        return tool_error(f"Failed to launch OSIRIS World Monitor: {e}")

registry.register(
    name="red_get_venture_report",
    toolset="red_core",
    schema=RED_GET_VENTURE_REPORT_SCHEMA,
    handler=lambda args, **kw: red_get_venture_report_tool(),
    emoji="[REPORT]",
)

registry.register(
    name="red_add_venture",
    toolset="red_core",
    schema=RED_ADD_VENTURE_SCHEMA,
    handler=lambda args, **kw: red_add_venture_tool(name=args.get("name", ""), description=args.get("description", "")),
    emoji="[VENTURE]",
)

registry.register(
    name="red_get_world_news",
    toolset="red_core",
    schema={"name": "red_get_world_news", "description": "Fetch live international news briefings concurrently."},
    handler=lambda args, **kw: red_get_world_news_tool(),
    emoji="[NEWS]",
)

registry.register(
    name="red_get_world_finance_news",
    toolset="red_core",
    schema={"name": "red_get_world_finance_news", "description": "Fetch live financial and market headlines concurrently."},
    handler=lambda args, **kw: red_get_world_finance_news_tool(),
    emoji="[FINANCE]",
)

registry.register(
    name="red_open_world_monitor",
    toolset="red_core",
    schema={"name": "red_open_world_monitor", "description": "Open live World Monitor dashboard."},
    handler=lambda args, **kw: red_open_world_monitor_tool(),
    emoji="[MONITOR]",
)

registry.register(
    name="red_open_finance_world_monitor",
    toolset="red_core",
    schema={"name": "red_open_finance_world_monitor", "description": "Open live Finance World Monitor dashboard."},
    handler=lambda args, **kw: red_open_finance_world_monitor_tool(),
    emoji="[MONITOR]",
)
