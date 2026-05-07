import sys
import os
import tkinter as tk


def main():
    root = tk.Tk()
    
    try:
        from gui import PDFToolkitGUI
        app = PDFToolkitGUI(root)
        root.mainloop()
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("\n请确保已安装所有依赖:")
        print("pip install -r requirements.txt")
        input("\n按 Enter 键退出...")
        sys.exit(1)
    except Exception as e:
        print(f"启动程序时出错: {e}")
        input("\n按 Enter 键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
