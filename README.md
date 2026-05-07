# 100 Tools - 效率工具集

一个精心打造的个人效率工具集合，包含三个实用工具，帮助你更高效地处理日常工作和内容创作。

## 📦 工具列表

| 工具 | 功能 | 技术栈 |
|------|------|--------|
| [HtmlToMd](#htmltomd---html--markdown-转换器) | 网页内容转 Markdown | Python + Tkinter |
| [MdToWechat](#mdtowechat---markdown-转微信公众号排版) | Markdown 转公众号排版 | HTML + JavaScript |
| [PdfTools](#pdftools---全功能-pdf-处理工具) | PDF 格式转换与编辑 | Python + Tkinter |

---

## 🛠️ HtmlToMd - HTML → Markdown 转换器

### 功能特性

- ✅ **URL 批量转换** - 一次最多转换 10 个网页链接
- ✅ **HTML 源码转换** - 直接粘贴 HTML 代码进行转换
- ✅ **智能标题提取** - 自动从 meta 或 title 标签提取标题
- ✅ **反爬处理** - 自动应对 JS 挑战、SPA 页面、安全验证等
- ✅ **图片处理** - 智能过滤垃圾图片，保留内容图片
- ✅ **跨平台打包** - 支持 Windows exe 和 macOS dmg

### 技术栈

```
requests==2.31.0           # HTTP 请求
markdownify==0.11.6       # HTML → Markdown 转换
beautifulsoup4==4.12.2   # HTML 解析
playwright==1.59.0        # 无头浏览器渲染
pyperclip==1.8.2          # 剪贴板操作
```

### 使用方法

```bash
# 安装依赖
cd HtmlToMd
pip install -r requirements.txt

# 运行程序
python main.py
```

---

## ✨ MdToWechat - Markdown 转微信公众号排版

### 功能特性

- ✅ **实时预览编辑** - 左右分栏，边写边看效果
- ✅ **文件上传** - 支持拖拽上传 .md / .txt 文件
- ✅ **5 种排版风格** - 经典笔记本、极简纯净、温暖纸张、现代科技、优雅杂志
- ✅ **5 种主题色** - 微信绿、商务蓝、活力橙、优雅紫、热情红
- ✅ **深色模式** - 支持浅色/深色主题切换
- ✅ **一键复制** - 富文本格式复制，粘贴即用

### 技术栈

```
marked.js 4.3.0     # Markdown 解析
highlight.js 11.9.0 # 代码语法高亮
纯 CSS + Vanilla JS # 无框架依赖
```

### 使用方法

直接在浏览器中打开 `index.html` 即可使用，无需安装任何依赖。

---

## 📄 PdfTools - 全功能 PDF 处理工具

### 功能特性

#### 格式转换
- ✅ **PDF 转图片** - PNG/JPG 格式，支持调节 DPI
- ✅ **图片转 PDF** - 多图合并为 PDF
- ✅ **PDF 转 Word** - 保留排版和图片
- ✅ **Word 转 PDF** - Word 文档转换

#### PDF 编辑
- ✅ **去除水印** - 智能识别并去除水印
- ✅ **添加水印** - 文字/图片水印
- ✅ **PDF 压缩** - 高/中/低三种压缩级别
- ✅ **PDF 加密/解密** - 密码保护

#### PDF 处理
- ✅ **PDF 合并** - 多文件合并
- ✅ **PDF 拆分** - 按范围/每N页拆分
- ✅ **PDF 旋转** - 90°/180°/270° 旋转
- ✅ **页面操作** - 提取/删除指定页面
- ✅ **内容提取** - 提取文本和图片

### 技术栈

```
pymupdf==1.24.0    # PDF 渲染和内容提取
pypdf==4.2.0       # PDF 结构操作
python-docx==1.1.0 # Word 文档生成
Pillow==10.3.0     # 图片处理
```

### 使用方法

```bash
# 安装依赖
cd PdfTools
pip install -r requirements.txt

# 运行程序
python main.py
```

---

## 🔧 项目结构

```
/workspace/
├── HtmlToMd/              # HTML → Markdown 转换器
│   ├── main.py            # 应用入口
│   ├── gui.py             # GUI 界面
│   ├── converter.py       # 转换核心
│   ├── fetcher.py         # 智能爬取
│   ├── requirements.txt   # 依赖
│   └── README.md          # 工具说明
│
├── MdToWechat/            # Markdown 转公众号排版
│   └── index.html         # 单页应用
│
├── PdfTools/              # 全功能 PDF 处理工具
│   ├── main.py            # 应用入口
│   ├── gui.py             # GUI 界面
│   ├── pdf_operations.py # PDF 操作核心
│   ├── requirements.txt   # 依赖
│   └── README.md          # 工具说明
│
└── README.md              # 本文件
```

## 🚀 工作流程

```
┌─────────────┐    HTML     ┌─────────────┐    Markdown   ┌─────────────┐
│   网页内容   │ ────────▶ │   HtmlToMd   │ ────────▶ │   MdToWechat │
│  (URL/HTML) │            │   Python     │            │   Web        │
└─────────────┘            └─────────────┘            └─────────────┘
                              保存 .md                   公众号排版
                                    │
                                    ▼
                              ┌─────────────┐
                              │   PdfTools   │
                              │   Python     │
                              └─────────────┘
                              处理本地 PDF

完整流程：网页内容 → Markdown → 公众号排版 / PDF 文档处理
```

## 📋 常见问题

### Q: 这些工具是免费的吗？
A: 是的，完全免费，可用于个人学习和日常工作。

### Q: 需要安装 Python 环境吗？
A: HtmlToMd 和 PdfTools 需要 Python 3.8+，MdToWechat 是纯前端工具，直接用浏览器打开即可。

### Q: 支持 macOS/Linux 吗？
A: HtmlToMd 和 PdfTools 支持 Python 环境的所有平台。MdToWechat 浏览器即可使用。

### Q: 文件处理是在本地完成的吗？
A: 是的，所有处理都在本地完成，不会上传到任何服务器。

## 🤝 贡献与反馈

如果你在使用过程中遇到问题或有好的建议，欢迎提交 Issue 或 Pull Request。

## 📄 许可证

本项目仅供个人学习交流使用，请勿用于商业用途。

---

**工具让工作更高效，让创作更简单！** 🚀

*最后更新: 2026-05-07*
