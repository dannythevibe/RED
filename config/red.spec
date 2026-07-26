# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('ui', 'ui'),
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
        'system.agentic.red_agentic_coder',
        'system.agentic.red_mcp_server',
        'system.agentic.red_tools',
        'system.cloud_sync.sync_engine',
        'system.cloud_sync.red_cloud_server'
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
