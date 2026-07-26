# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

def collect_ui_without_node_modules():
    ui_files = []
    for root, dirs, files in os.walk('ui'):
        # Skip node_modules and .git directories
        path_parts = os.path.normpath(root).split(os.sep)
        if 'node_modules' in path_parts or '.git' in path_parts:
            continue
        for file in files:
            full_path = os.path.join(root, file)
            # Target dir inside package
            dest_dir = os.path.normpath(root)
            ui_files.append((full_path, dest_dir))
    return ui_files

added_files = collect_ui_without_node_modules() + [
    ('config', 'config'),
    ('system', 'system'),
    ('knowledge', 'knowledge'),
    ('polymath_core', 'polymath_core'),
    ('compression', 'compression'),
    ('core', 'core')
]

a = Analysis(
    ['red.py'],
    pathex=['.', 'system/agentic/agent_engine'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'edge_tts',
        'pygame',
        'asyncio',
        'aiohttp',
        'mss',
        'PIL',
        'requests',
        'speech_recognition',
        'json',
        'queue',
        'threading',
        'fastapi',
        'uvicorn',
        'sqlite3',
        'subprocess',
        'pydantic',
        'system.ai.groq_engine',
        'system.ai.red_ollama',
        'system.audio.red_audio_stream',
        'system.audio.dictation_service',
        'system.vision.red_vision',
        'system.vision.red_gesture',
        'system.agentic.red_agentic_coder',
        'system.agentic.red_mcp_server',
        'system.agentic.red_tools',
        'system.cloud_sync.sync_engine',
        'system.cloud_sync.red_cloud_server',
        'system.memory.red_conversation_memory',
        'system.memory.red_transcript_engine',
        'system.memory.red_action_extractor',
        'httpx',
        'fastmcp',
        'mediapipe',
        'cv2',
        'pystray',
        'playwright'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow',
        'tensorboard',
        'keras',
        'tf_keras',
        'h5py',
        'PyQt6',
        'PySide6',
        'PyQt5',
        'PySide2',
        'matplotlib',
        'notebook',
        'ipython'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RED',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/red_logo.ico',
    uac_admin=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RED_DIST',
)
