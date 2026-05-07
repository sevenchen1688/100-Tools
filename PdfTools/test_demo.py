#!/usr/bin/env python3
import sys
import os

print("=" * 60)
print("🖥️  PDF Toolkit 功能测试")
print("=" * 60)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n[1/4] 正在加载模块...")
try:
    from pdf_operations import PDFOperations
    print("    ✓ pdf_operations 模块加载成功")
except Exception as e:
    print(f"    ✗ 模块加载失败: {e}")
    sys.exit(1)

print("\n[2/4] 正在验证 GUI 模块...")
try:
    from gui import PDFToolkitGUI, FUNCTIONS, C
    print(f"    ✓ gui 模块加载成功")
    print(f"    ✓ 共 {len(FUNCTIONS)} 个功能模块")
except Exception as e:
    print(f"    ✗ GUI 模块加载失败: {e}")
    sys.exit(1)

print("\n[3/4] 功能列表:")
for i, func in enumerate(FUNCTIONS, 1):
    print(f"    {i:2d}. {func['icon']} {func['name']:12s} - {func['desc']}")

print("\n[4/4] PDFOperations 类方法:")
ops = PDFOperations()
methods = [m for m in dir(ops) if not m.startswith('_') and callable(getattr(ops, m))]
for i, method in enumerate(methods, 1):
    print(f"    {i:2d}. {method}")

print("\n" + "=" * 60)
print("✅ 所有模块验证通过！")
print("=" * 60)
print("\n📋 使用说明:")
print("   1. 在有图形界面的环境中运行: python main.py")
print("   2. 或双击运行打包后的可执行文件")
print("=" * 60)
