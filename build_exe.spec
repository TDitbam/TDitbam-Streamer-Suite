# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ('icon.ico', '.'),
    ('resources', 'resources'),
]

# Ensure external dependencies that might have hidden imports are included
hidden_imports = [
    'pytchat',
    'TikTokLive',
    'edge_tts',
    'deep_translator',
    'pygame',
    'gtts',
    'psutil',
    'customtkinter',
    'pystray',
    'PIL'
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='StreamerSuite',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon='icon.ico',
    contents_directory='parts',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StreamerSuite',
)
