# -*- mode: python ; coding: utf-8 -*-


datas = [('7z.exe', '.')]
binaries = []
# 确保包含我们的 qt_progress 模块和 PyQt5 子模块
#hiddenimports = ['qt_progress', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui']
#excludes = ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', '_tkinter', 'PIL', 'matplotlib']

# 不包含 Qt 相关模块，构建为控制台 exe（不打包 PyQt5/qt_progress）
hiddenimports = []
excludes = ['tkinter', 'tkinter.ttk', 'tkinter.messagebox', '_tkinter', 'PIL', 'matplotlib', 'PyQt5', 'qt_progress']


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
    # 使用控制台模式，这样在没有 GUI 的机器上会以控制台方式运行
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='titizz_icon.ico',  # 添加图标
)
