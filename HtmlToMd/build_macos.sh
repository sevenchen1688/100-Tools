#!/bin/bash
set -e

echo "============================================================"
echo "  HTML to Markdown - macOS 打包构建脚本"
echo "============================================================"
echo

cd "$(dirname "$0")"

echo "[1/5] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi
echo "✅ Python 环境正常"

echo
echo "[2/5] 检查 PyInstaller..."
python3 -c "import PyInstaller" 2>/dev/null || {
    echo "正在安装 PyInstaller..."
    pip3 install pyinstaller
}
echo "✅ PyInstaller 就绪"

echo
echo "[3/5] 安装项目依赖..."
pip3 install -r requirements.txt
echo "✅ 依赖安装完成"

echo
echo "[4/5] 开始打包..."
echo "  - 模式: macOS .app 应用"
echo "  - 控制台: 隐藏 (windowed)"

rm -rf dist/HtmlToMd.app build/ 2>/dev/null || true

pyinstaller --noconfirm \
    --name "HtmlToMd" \
    --windowed \
    --onedir \
    --add-data "converter.py:." \
    --add-data "fetcher.py:." \
    --add-data "gui.py:." \
    --hidden-import markdownify \
    --hidden-import bs4 \
    --hidden-import requests \
    --hidden-import pyperclip \
    --hidden-import playwright \
    --hidden-import playwright.sync_api \
    --hidden-import playwright._impl \
    --hidden-import playwright._impl._driver \
    --hidden-import greenlet \
    --exclude-module tkinter.test \
    --exclude-module unittest \
    --exclude-module numpy \
    --exclude-module pandas \
    --exclude-module matplotlib \
    --exclude-module PIL \
    --exclude-module PyQt5 \
    --exclude-module PyQt6 \
    --exclude-module PySide2 \
    --exclude-module PySide6 \
    main.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ 打包失败，请检查错误信息"
    exit 1
fi

echo
echo "[5/5] 创建 DMG 安装镜像..."

APP_DIR="dist/HtmlToMd.app"
DMG_DIR="dist/dmg_staging"
DMG_NAME="HtmlToMd-macOS.dmg"
DMG_VOLUME="HtmlToMd"

rm -rf "$DMG_DIR" "$DMG_NAME" 2>/dev/null || true

mkdir -p "$DMG_DIR"
cp -R "$APP_DIR" "$DMG_DIR/"

ln -s /Applications "$DMG_DIR/Applications"

cat > "$DMG_DIR/安装浏览器引擎.command" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
echo "正在安装 Playwright Chromium 浏览器引擎..."
echo "此操作仅需执行一次，下载约 200MB"
echo
PLAYWRIGHT_BROWSERS_PATH="$(dirname "$0")/HtmlToMd.app/Contents/MacOS/browsers" \
    ./HtmlToMd.app/Contents/MacOS/HtmlToMd --install-browsers
echo
echo "安装完成！"
read -p "按回车键退出..."
SCRIPT
chmod +x "$DMG_DIR/安装浏览器引擎.command"

hdiutil create -volname "$DMG_VOLUME" \
    -srcfolder "$DMG_DIR" \
    -ov -format UDZO \
    "$DMG_NAME"

rm -rf "$DMG_DIR"

echo
echo "============================================================"
echo "  ✅ 打包完成！"
echo
echo "  .app 路径: $(pwd)/dist/HtmlToMd.app"
echo "  .dmg 路径: $(pwd)/$DMG_NAME"
echo
echo "  注意事项:"
echo "  1. 首次使用时如需渲染 JS 网页，请先运行'安装浏览器引擎.command'"
echo "  2. DMG 可直接分发给 macOS 用户"
echo "  3. Playwright 浏览器引擎不包含在包中，需用户自行安装"
echo "============================================================"

DMG_SIZE=$(du -sh "$DMG_NAME" | cut -f1)
echo "DMG 大小: $DMG_SIZE"
