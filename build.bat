@echo off
REM 简化构建脚本 (Windows cmd)
REM 用法: 在项目根目录下运行: build.bat

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️ 未找到虚拟环境激活脚本 .venv\Scripts\activate.bat
)

if exist titizz_icon_full.ico (
    if exist titizz_icon.ico (
        copy /Y titizz_icon.ico titizz_icon.ico.smallbak >nul
        echo ✅ 备份现有图标到 titizz_icon.ico.smallbak
    )
    copy /Y titizz_icon_full.ico titizz_icon.ico >nul
    echo ✅ 使用 titizz_icon_full.ico 替换 titizz_icon.ico
)

echo 🔨 运行 build_tool.py...
python build_tool.py
if errorlevel 1 (
    echo ❌ 构建失败
    exit /b 1
)

echo ✨ 构建完成
exit /b 0
