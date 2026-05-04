@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ============================================================
echo   HTML to Markdown - Windows 打包构建脚本
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/5] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)
echo ✅ Python 环境正常

echo.
echo [2/5] 检查 PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)
echo ✅ PyInstaller 就绪

echo.
echo [3/5] 安装项目依赖...
pip install -r requirements.txt
echo ✅ 依赖安装完成

echo.
echo [4/5] 开始打包...
echo   - 模式: 目录打包 (COLLECT)
echo   - 控制台: 隐藏 (windowed)
echo   - UPX 压缩: 启用

if exist "dist\HtmlToMd" (
    echo 正在清理旧的构建产物...
    rmdir /s /q "dist\HtmlToMd" 2>nul
)
if exist "build" (
    rmdir /s /q "build" 2>nul
)

pyinstaller --noconfirm HtmlToMd.spec

if errorlevel 1 (
    echo.
    echo ❌ 打包失败，请检查错误信息
    pause
    exit /b 1
)

echo.
echo [5/5] 创建启动脚本...

set "DIST_DIR=dist\HtmlToMd"

echo @echo off > "%DIST_DIR%\安装浏览器引擎.bat"
echo chcp 65001 ^>nul >> "%DIST_DIR%\安装浏览器引擎.bat"
echo echo 正在安装 Playwright Chromium 浏览器引擎... >> "%DIST_DIR%\安装浏览器引擎.bat"
echo echo 此操作仅需执行一次，下载约 200MB >> "%DIST_DIR%\安装浏览器引擎.bat"
echo set PLAYWRIGHT_BROWSERS_PATH=%%~dp0browsers >> "%DIST_DIR%\安装浏览器引擎.bat"
echo HtmlToMd.exe --install-browsers >> "%DIST_DIR%\安装浏览器引擎.bat"
echo echo. >> "%DIST_DIR%\安装浏览器引擎.bat"
echo echo 安装完成！现在可以正常使用 HtmlToMd.exe >> "%DIST_DIR%\安装浏览器引擎.bat"
echo pause >> "%DIST_DIR%\安装浏览器引擎.bat"

echo.
echo ============================================================
echo   ✅ 打包完成！
echo.
echo   输出目录: %CD%\dist\HtmlToMd\
echo   主程序:   HtmlToMd.exe
echo.
echo   注意事项:
echo   1. 首次使用时如需渲染 JS 网页，请先运行"安装浏览器引擎.bat"
echo   2. 可将 dist\HtmlToMd 文件夹压缩为 zip 分发
echo   3. Playwright 浏览器引擎不包含在包中，需用户自行安装
echo ============================================================
echo.

for %%A in ("%DIST_DIR%") do set "SIZE=0"
for /r "%DIST_DIR%" %%F in (*) do (
    set /a "SIZE+=%%~zF/1024"
)
echo 包大小: 约 !SIZE! KB

pause
