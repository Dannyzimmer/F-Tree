# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("resources/parameters.json", "."),
        ("resources/database/*", "database"),
        ("resources/img/*", "img"),
        ("resources/lang/*", "lang"),
        ("resources/style/*", "style")
    ],
    hiddenimports=[
        'PIL._tkinter_finder',
        '_tkinter',
        'PySide6',
        'weasyprint'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='F-Tree',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    contents_directory='resources',
    icon='resources/img/fcode_tree_full_icon_dark_mode.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='run',
)
