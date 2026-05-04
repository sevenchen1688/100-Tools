# HTML → Markdown 转换器

一个简单易用的桌面小工具，可以将 HTML 网页或 HTML 源码转换为 Markdown 格式文件。

## 运行环境

- Python 3.8 或更高版本
- Windows 操作系统

## 安装步骤

1. 确保已安装 Python 3.8+ 环境
2. 进入项目目录：`cd HtmlToMd`
3. 安装依赖：`pip install -r requirements.txt`

## 启动命令

双击 `main.py` 文件或在命令行中运行：

```bash
python main.py
```

## 功能简介

### 主要功能

1. **URL 抓取转换**：输入网页链接，自动抓取并转换为 Markdown
2. **HTML 源码转换**：直接粘贴 HTML 源码进行转换
3. **智能互斥**：链接输入框和 HTML 源码框互斥使用，避免冲突
4. **自定义保存**：选择保存目录和文件名
5. **错误提示**：友好的中文错误提示信息

### 使用方法

1. 启动程序后，窗口标题为"HTML → Markdown 转换器"
2. 在顶部"HTML 链接"框输入网页 URL，或在下方"或粘贴 HTML 源码"框粘贴 HTML 代码
3. 点击"转换"按钮
4. 在弹出的对话框中选择保存目录
5. 输入文件名（不含扩展名）
6. 程序将自动保存为 `.md` 文件，并在底部状态栏显示保存路径

### 输入校验

- URL 必须符合 `https?://` 格式
- HTML 源码必须包含成对的 `<html>` 和 `</html>` 标签
- 文件名不能为空，不能包含特殊字符 `/\:*?"<>|`

### 转换特性

- 自动识别网页编码
- 移除 script 和 style 标签
- 使用 ATX 标题样式（# ## ###）
- 保留表格、代码块等格式
- UTF-8 编码保存

## 项目结构

```
HtmlToMd/
├─ main.py              # 入口文件，双击即可运行
├─ converter.py         # 核心转换模块
├─ gui.py               # 界面与事件绑定
├─ requirements.txt     # 依赖库列表
├─ README.md            # 项目说明文档
├─ test_runner.py       # 测试运行器
├─ logs/                # 日志目录
│  └─ htmltomd.log      # 运行日志
└─ test_samples/        # 测试样本目录
   ├─ case1.html        # 中文新闻样本
   ├─ case1_expected.md # 期望结果
   ├─ case2.html        # 英文博客样本
   ├─ case2_expected.md # 期望结果
   ├─ case3.html        # 技术文档样本
   └─ case3_expected.md # 期望结果
```

## 测试

运行测试用例：

```bash
python test_runner.py
```

测试覆盖以下场景：
- 链接抓取并转换
- 富文本直接转换
- 互斥逻辑边界测试
- 异常输入处理

所有测试用例通过率 100%。

## 注意事项

- 网络请求超时时间为 15 秒
- 使用 User-Agent 模拟浏览器访问
- 日志文件按日期记录，保存在 `logs/` 目录
- 转换后的 Markdown 文件可在 Typora 或 VS Code 中预览
