# -*- mode: python ; coding: utf-8 -*-

datas = [('7z.exe', '.')]
binaries = []
hiddenimports = []
excludes = ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', '_tkinter', 'PIL', 'matplotlib']


a = Analysis(
    ['titizz_extract.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='titizz_extract',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='titizz_icon.ico',  # 添加图标
)
