import sys
import os


def install_browsers():
    from fetcher import _ensure_playwright_browsers, _get_app_dir
    import logging

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)

    print("正在安装 Playwright Chromium 浏览器引擎...")
    print(f"安装路径: {_get_app_dir() / 'browsers'}")
    print("此操作仅需执行一次，下载约 200MB\n")

    success = _ensure_playwright_browsers(logger)
    if success:
        print("\n✅ 浏览器引擎安装完成！现在可以正常使用 HtmlToMd。")
    else:
        print("\n❌ 安装失败，请检查网络连接后重试。")
    return success


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--install-browsers':
            install_browsers()
            return

    import tkinter as tk
    from gui import HTMLToMarkdownGUI

    root = tk.Tk()
    app = HTMLToMarkdownGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
