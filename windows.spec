# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_dynamic_libs

import os
import glob

# Get the `WINDOWS_RESOURCES_DIR` from the environment variable
windows_resources_dir = os.getenv('WINDOWS_RESOURCES_DIR', 'Z:\\opt\\development\\resources\\ftree\\windows_resources')

graphviz_bin_path = windows_resources_dir + '\\Graphviz-12.1.2-win64\\bin'

# Collect all binaries (DLLs, executables, etc.) from the Graphviz bin folder
graphviz_binaries = [(file, 'graphviz_bin') for file in glob.glob(os.path.join(graphviz_bin_path, '*'))]

# Path to the correct tcl86t.dll for your application (this is the version that works without Graphviz)
app_tcl86t_dll = windows_resources_dir + '\\tcl86t.dll'

# Set up the binaries and add also GObject library from GTK3 runtime
binaries = [
    ('C:\\Program Files\\GTK3-Runtime Win64\\bin\\libcairo-gobject-2.dll','.'),
    (app_tcl86t_dll, '.'),  # Correct tcl86t.dll for your app in the root
    *graphviz_binaries      # Graphviz binaries in graphviz_bin
]

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ("resources/parameters.json", "."),
        ("resources/version", "."),
        ("resources/database/*", "database"),
        ("resources/img/*", "img"),
        ("resources/lang/*", "lang"),
        ("resources/style/*", "style"),
        ("examples", "examples"),
        ("LICENSE", "."),
        (windows_resources_dir + '\\CREDITS.txt', "."),
        (windows_resources_dir + '\\Graphviz-12.1.2-win64\\LICENSE.graphviz.txt', "third_party_licenses")
    ],
    hiddenimports=[
        'PIL._tkinter_finder', 
        '_tkinter'
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
    console=False,
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
    name='bundle_windows',
)
