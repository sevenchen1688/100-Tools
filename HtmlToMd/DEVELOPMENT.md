# HTML → Markdown 批量转换器 — 开发过程文档

> 项目名称：HTML → Markdown 批量转换器  
> 开发周期：2026年4月 — 2026年5月  
> 技术栈：Python 3.14 / Tkinter / Playwright / BeautifulSoup / PyInstaller  
> 项目路径：`D:\Developer\100个小工具\HtmlToMd`

---

## 目录

1. [开发过程 Prompt 记录](#1-开发过程-prompt-记录)
2. [错误、问题与挑战](#2-错误问题与挑战)
3. [关键决策与技术选型](#3-关键决策与技术选型)
4. [最终成品展示](#4-最终成品展示)
5. [测试情况](#5-测试情况)
6. [项目文件结构](#6-项目文件结构)

---

## 1. 开发过程 Prompt 记录

### Prompt 1：初始功能开发

**时间**：第一阶段  
**目的**：创建 HTML 文章内容转 Markdown 文件的桌面工具  
**上下文**：项目从零开始，需要实现核心转换功能

> 创建一个"HTML 文章内容 → Markdown 文件"的桌面工具，支持 URL 抓取和 HTML 源码粘贴两种输入方式，自动提取标题，输出 .md 文件。

**产出**：`converter.py`、`gui.py`、`main.py` 初始版本

---

### Prompt 2：JS 反爬验证问题

**时间**：第二阶段  
**目的**：修复人社部官网抓取失败问题  
**上下文**：测试 URL `https://www.mohrss.gov.cn/...` 返回的是 JavaScript 代码而非页面内容

> 测试一下抓取链接，转成md文件，链接如下：`https://www.mohrss.gov.cn/SYrlzyhshbzb/dongtaixinwen/shizhengyaowen/202604/t20260430_575288.html`，转成的md文件不对，内容是 JavaScript 代码，请分析并解决。

**产出**：JS 挑战检测机制，Node.js 自动解析 Cookie 验证

---

### Prompt 3：SPA 单页应用问题

**时间**：第二阶段  
**目的**：修复笔记分享网站抓取失败问题  
**上下文**：`https://biji.com/note/share_note/...` 是 SPA 应用，HTML body 为空

> `https://biji.com/note/share_note/5Jrk26YgRwXBR` 测试这个url，还是获取不到内容。

**产出**：SPA 检测机制，Playwright 无头浏览器渲染回退

---

### Prompt 4：批量转换功能

**时间**：第三阶段  
**目的**：增加批量 URL 转换能力  
**上下文**：用户需要同时处理多个网页链接

> 请为系统增加批量转换功能，具体要求如下：1) 支持多行URL输入；2) 自动提取标题作为文件名；3) 重名文件自动编号；4) 进度条显示；5) 结果区域展示转换状态；6) 最多支持10个链接；7) URL和HTML输入互斥。

**产出**：批量转换 UI、进度条、结果面板、互斥输入逻辑

---

### Prompt 5：GUI 文字重影修复

**时间**：第四阶段  
**目的**：修复 GUI 界面文字重影视觉异常  
**上下文**：在 GUI 界面上观察到文字总结区域出现明显的重影现象

> 在GUI界面上观察到文字总结区域出现了明显的重影现象。请对该视觉异常进行全面排查与修复。

**产出**：SectionCard 双重 padding 移除、highlightthickness 优化、系统字体适配

---

### Prompt 6：百度安全验证问题

**时间**：第五阶段  
**目的**：修复百度百家号文章抓取失败问题  
**上下文**：`https://baijiahao.baidu.com/...` 返回"百度安全验证"页面

> `https://baijiahao.baidu.com/s?id=1864172176914224450&wfr=spider&for=pc` 开放链接的还是获取不到，请检查原因。

**产出**：安全验证页面检测机制，Playwright 渲染回退

---

### Prompt 7：百度安全验证深度排查

**时间**：第五阶段  
**目的**：对百度安全验证问题进行系统性排查  
**上下文**：需要全面分析百度安全验证的触发条件和绕过方案

> 针对网页 `https://baijiahao.baidu.com/s?id=1864172176914224450&wfr=spider&for=pc` 出现的"百度安全验证 网络不给力，请稍后重试"问题，请执行以下检查与分析：1) 检查当前请求头配置；2) 分析安全验证触发条件；3) 测试 Playwright 渲染效果；4) 评估反爬策略；5) 提出解决方案；6) 验证修复效果。

**产出**：Playwright 隐身模式、人类行为模拟、随机视口尺寸

---

### Prompt 8：SmartFetcher 智能爬取模块

**时间**：第六阶段  
**目的**：开发通用网页内容爬取解决方案  
**上下文**：需要系统性地应对各类反爬机制

> 针对部分网站无法正常爬取内容的问题，开发一个网页内容爬取解决方案，要求能够兼容并处理大部分常见的反爬取情况。该方案需要识别并应对包括但不限于以下反爬机制：动态JavaScript渲染、请求头验证、IP限制、Cookie验证、验证码机制、User-Agent检测、频率限制等。实现时应包含多种应对策略，如使用无头浏览器模拟真实用户行为、自动轮换IP地址、随机生成合规请求头、智能处理Cookie、集成验证码识别服务、实现请求频率控制等功能。确保解决方案能够稳定、高效地爬取目标网站内容，同时遵守目标网站的robots协议和相关法律法规。提供详细的配置说明、使用文档和测试报告，验证方案在不同类型网站上的兼容性和有效性。

**产出**：`fetcher.py` — SmartFetcher 完整模块，包含 UA 轮换池、请求频率控制、JS 挑战解决、SPA 检测、安全验证检测、CAPTCHA 检测、Playwright 隐身渲染、robots.txt 遵守

---

### Prompt 9：图片爬取问题排查与修复

**时间**：第七阶段  
**目的**：修复 cac.gov.cn 网页图片未被爬取的问题  
**上下文**：转换结果中图片完全丢失

> 对网页 `https://www.cac.gov.cn/2026-05/03/c_1779551202311487.htm` 进行图片爬取问题排查与修复。具体任务包括：1) 访问指定网页并定位未被爬取到的目标图片元素；2) 分析导致图片爬取失败的可能原因；3) 针对具体原因实施技术解决方案；4) 验证修复效果确保目标图片能够被成功爬取；5) 提供问题分析报告及解决过程说明。

**产出**：`_is_junk_image()` 垃圾图片智能过滤、`_process_images()` 图片预处理（URL 修复、懒加载支持、alt 文本生成）、移除破坏性正则

---

### Prompt 10：打包为可执行文件

**时间**：第八阶段  
**目的**：将工具打包为 Windows exe 和 macOS dmg  
**上下文**：用户希望不依赖 Python 环境直接运行

> 我需要把这个工具打包成Windows直接可执行的exe文件以及mac系统可直接安装执行的dmg格式文件。

**产出**：`HtmlToMd.spec`、`build_windows.bat`、`build_macos.sh`、Playwright 浏览器首次运行自动安装机制、`--install-browsers` 命令行参数

---

## 2. 错误、问题与挑战

### 2.1 JS 反爬验证 — 人社部官网

| 项目 | 详情 |
|------|------|
| **错误现象** | 抓取 `mohrss.gov.cn` 返回 JavaScript 代码，而非页面 HTML 内容 |
| **根本原因** | 网站使用 JS Cookie 挑战机制，首次访问时返回含 `__tst_status` 等变量的 JS 代码，浏览器执行后设置 Cookie 才能获取真实页面 |
| **排查过程** | 1) 对比浏览器和 requests 返回内容；2) 分析 JS 代码发现 Cookie 设置逻辑；3) 尝试直接携带 Cookie 重试 |
| **解决方案** | 实现 `_is_js_challenge()` 检测 + `_solve_js_challenge()` 通过 Node.js 执行 JS 获取 Cookie + Playwright 回退 |
| **最终结果** | ✅ 人社部官网可正常抓取 |

### 2.2 SPA 单页应用 — biji.com

| 项目 | 详情 |
|------|------|
| **错误现象** | 抓取 `biji.com` 返回的 HTML body 几乎为空，只有 `<div id="app">` 和 JS 脚本 |
| **根本原因** | SPA 应用通过 JavaScript 动态渲染内容，requests 只能获取初始空壳 HTML |
| **排查过程** | 1) 检查返回 HTML 长度；2) 发现 body 文本 < 300 字符；3) 识别 `div#app` + script 标签模式 |
| **解决方案** | 实现 `_is_spa_page()` 检测（body 文本 < 300 + `div#app/root` + script 标签），自动回退到 Playwright 渲染 |
| **最终结果** | ✅ SPA 页面可通过 Playwright 正常渲染 |

### 2.3 百度安全验证

| 项目 | 详情 |
|------|------|
| **错误现象** | 抓取 `baijiahao.baidu.com` 返回"百度安全验证 — 网络不给力，请稍后重试"页面 |
| **根本原因** | 百度检测到非浏览器请求特征（缺少完整浏览器指纹、WebDriver 特征暴露等），触发安全验证 |
| **排查过程** | 1) 检查请求头配置；2) 发现缺少 Sec-Fetch-* 系列头；3) Playwright 默认配置暴露 `navigator.webdriver`；4) 视口尺寸过于固定 |
| **解决方案** | 1) 添加完整 Sec-Fetch-* 请求头；2) Playwright 隐身模式（隐藏 webdriver、伪造 plugins/languages/chrome）；3) 随机视口尺寸；4) 人类行为模拟（随机等待时间） |
| **最终结果** | ✅ 百度百家号文章可正常抓取 |

### 2.4 GUI 文字重影

| 项目 | 详情 |
|------|------|
| **错误现象** | GUI 界面文字总结区域出现明显的重影/残影现象 |
| **根本原因** | 多重因素叠加：1) SectionCard 存在双重 padding；2) highlightthickness 过大导致边框重绘异常；3) 非系统字体渲染不一致 |
| **排查过程** | 1) 逐组件检查 padding 设置；2) 测试不同 highlightthickness 值；3) 对比系统字体与自定义字体渲染效果 |
| **解决方案** | 1) 移除 SectionCard 双重 padding；2) 将 highlightthickness 设为 1；3) 使用 Microsoft YaHei UI 系统字体 |
| **最终结果** | ✅ 重影现象消除 |

### 2.5 图片爬取丢失 — cac.gov.cn

| 项目 | 详情 |
|------|------|
| **错误现象** | 转换后的 Markdown 文件中所有图片消失 |
| **根本原因** | **致命 Bug**：`converter.py` 第 137 行的正则 `re.sub(r'!\[\]\([^)]*\)\s*', '', markdown_text)` 会删除所有空 alt 的图片。而绝大多数网页内容图片的 alt 属性恰好为空。此外，图片 URL 使用协议相对路径 `//` 未被转换为绝对路径 |
| **排查过程** | 1) 抓取原始 HTML 确认图片元素存在（19 个 img 标签）；2) 在 `_clean_html` 后确认内容区域有 2 张图片；3) 在 markdownify 后确认 2 张图片被正确转换；4) 在正则清理后确认 0 张图片 — 定位到破坏性正则 |
| **解决方案** | 1) 删除破坏性正则；2) 新增 `_is_junk_image()` 基于 src/class/parent-class/尺寸智能过滤垃圾图片；3) 新增 `_process_images()` 统一处理图片（URL 修复、懒加载支持、alt 文本生成）；4) `source_url` 参数贯穿调用链 |
| **最终结果** | ✅ 2 张内容图片成功保留，17 张垃圾图片正确过滤 |

### 2.6 Playwright 浏览器打包

| 项目 | 详情 |
|------|------|
| **错误现象** | Playwright Chromium 浏览器引擎约 675MB，直接打包进 exe/dmg 不现实 |
| **根本原因** | Chromium 浏览器二进制文件体积巨大，且跨平台二进制不兼容 |
| **排查过程** | 1) 检查浏览器安装路径 `C:\Users\...\AppData\Local\ms-playwright`；2) 计算总大小 675MB；3) 评估打包后体积影响 |
| **解决方案** | 首次运行自动安装策略：1) `_is_frozen()` 检测打包环境；2) `_get_app_dir()` 定位应用目录；3) `_ensure_playwright_browsers()` 自动安装到 `browsers/` 子目录；4) 提供 `--install-browsers` 命令行参数和辅助脚本 |
| **最终结果** | ✅ 打包后体积 129.4MB，浏览器按需安装 |

---

## 3. 关键决策与技术选型

### 3.1 GUI 框架选择：Tkinter

| 选项 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| Tkinter | Python 内置、无需额外依赖、跨平台、轻量 | 原生控件较简陋 | ✅ 选择 |
| PyQt/PySide | 控件丰富、现代外观 | 体积大（~50MB+）、许可证复杂、打包体积膨胀 | ❌ 排除 |
| DearPyGui | GPU 渲染、性能好 | 生态较小、学习成本高 | ❌ 排除 |

**理由**：Tkinter 是 Python 标准库组件，零额外依赖，打包体积最小。通过自定义 Canvas 绘制渐变头、自定义 Frame 实现动画按钮等方式弥补了原生控件的外观不足。

### 3.2 HTML 解析：BeautifulSoup + markdownify

| 选项 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| BeautifulSoup + markdownify | 成熟稳定、API 简洁、容错性强 | 速度较慢 | ✅ 选择 |
| lxml + html2text | 速度快 | lxml C 扩展打包复杂、html2text 输出格式不稳定 | ❌ 排除 |
| pypandoc | 功能最全 | 依赖外部 Pandoc 二进制 | ❌ 排除 |

**理由**：BeautifulSoup 对不规范 HTML 的容错能力极强，markdownify 输出格式稳定可控。两者均为纯 Python 实现，打包无障碍。

### 3.3 反爬策略：分层检测 + 渐进回退

```
请求流程：
requests 直接请求
    ↓ 失败/检测到反爬
JS 挑战检测 → Node.js 解析 Cookie → 携带 Cookie 重试
    ↓ 仍失败
SPA 检测 → Playwright 渲染
安全验证检测 → Playwright 隐身渲染
CAPTCHA 检测 → Playwright 渲染
```

**理由**：直接请求速度最快（< 1s），Playwright 渲染较慢（3-8s）。分层检测确保简单页面不走重路径，复杂页面自动回退。

### 3.4 图片处理策略：智能过滤 + URL 修复

| 策略 | 说明 |
|------|------|
| 垃圾图片过滤 | 基于 src/class/parent-class 中的关键词（logo、icon、banner、qr 等）+ 尺寸阈值（< 50px） |
| URL 协议修复 | `//` → `https://`，`/path` → 拼接 base_url，相对路径 → `urljoin()` |
| 懒加载支持 | 优先使用 `data-src`/`data-original`/`data-lazy-src` 替代空 `src` |
| alt 文本生成 | 空 alt 时从文件名提取描述，或使用通用"图片"文本 |

**理由**：原方案（删除空 alt 图片正则）过于粗暴，误杀所有内容图片。新方案通过语义分析区分垃圾图片和内容图片，同时修复 URL 确保图片在 Markdown 中可正常显示。

### 3.5 打包策略：Playwright 浏览器按需安装

| 选项 | 优势 | 劣势 | 决策 |
|------|------|------|------|
| 内置浏览器 | 开箱即用 | 包体积 800MB+ | ❌ 排除 |
| 按需安装 | 包体积仅 130MB | 首次使用需下载 | ✅ 选择 |
| 不支持 Playwright | 包体积最小 | 丧失 JS 渲染能力 | ❌ 排除 |

**理由**：大多数网页不需要 Playwright 渲染，按需安装策略在体积和功能之间取得最佳平衡。

---

## 4. 最终成品展示

### 4.1 功能说明

| 功能 | 描述 |
|------|------|
| URL 批量转换 | 支持一次输入最多 10 个 URL，自动抓取并转换为 Markdown |
| HTML 源码转换 | 支持直接粘贴 HTML 源码进行单次转换 |
| 智能标题提取 | 从 meta 标签或 title 标签自动提取文章标题作为文件名 |
| 反爬处理 | 自动检测并应对 JS 挑战、SPA、安全验证、CAPTCHA 等反爬机制 |
| 图片保留 | 智能过滤垃圾图片，保留内容图片，修复 URL，生成 alt 文本 |
| 进度显示 | 实时进度条 + 状态指示灯 + 结果面板 |
| 互斥输入 | URL 和 HTML 输入互斥，防止误操作 |
| 跨平台打包 | Windows exe + macOS dmg |

### 4.2 使用方法

**源码运行：**

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器（可选，用于 JS 渲染）
python -m playwright install chromium

# 启动 GUI
python main.py
```

**Windows exe 运行：**

```
1. 双击 HtmlToMd.exe 启动 GUI
2. 如需 JS 渲染功能，先运行"安装浏览器引擎.bat"
```

**macOS dmg 运行：**

```
1. 打开 HtmlToMd-macOS.dmg
2. 将 HtmlToMd.app 拖入 Applications
3. 如需 JS 渲染功能，先运行"安装浏览器引擎.command"
```

### 4.3 界面布局

```
┌─────────────────────────────────────────────────────────┐
│  ██████ 渐变头: HTML → Markdown 批量转换器 ██████       │
├─────────────────────────────────────────────────────────┤
│  🔗 批量链接输入 (每行一个链接，最多10个)               │
│  ┌─────────────────────────────────────────────┐ 0/10  │
│  │ https://example.com/article1                │       │
│  │ https://example.com/article2                │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  📝 或粘贴 HTML 源码 (单个转换模式)                     │
│  ┌─────────────────────────────────────────────┐       │
│  │                                             │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  📁 输出目录                                            │
│  ┌──────────────────────────────────┐ [📂 选择目录]    │
│  │ C:\Users\...\output              │                   │
│  └──────────────────────────────────┘                   │
│                                                         │
│  [▶ 开始批量转换]  🟢 就绪                              │
│                                                         │
│  📊 转换进度                                            │
│  ████████████████████░░░░░░░░ 75%                      │
│  ┌─────────────────────────────────────────────┐       │
│  │ ✅ 文章标题1 → C:\...\output\文章标题1.md    │       │
│  │ ✅ 文章标题2 → C:\...\output\文章标题2.md    │       │
│  │ ⏳ 处理中: https://example.com/article3     │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

### 4.4 核心代码片段

#### SmartFetcher 反爬检测流程

```python
def fetch(self, url: str) -> str:
    session = requests.Session()
    try:
        response = self._request_with_retry(session, url, {})
        html = response.text
    except Exception as e:
        return self._render_with_playwright(url)

    if self._is_js_challenge(html):
        cookies = self._solve_js_challenge(html)
        if cookies:
            # 携带 Cookie 重试
            ...
        return self._render_with_playwright(url)

    if self._is_spa_page(html):
        return self._render_with_playwright(url)

    if self._is_security_verification(html):
        return self._render_with_playwright(url)

    if self._is_captcha_page(html):
        return self._render_with_playwright(url)

    return html
```

#### 图片智能处理

```python
def _process_images(self, content_element, source_url=''):
    for img in content_element.find_all('img'):
        if self._is_junk_image(img):
            img.decompose()
            continue

        # 懒加载支持：优先使用 data-src
        actual_src = img.get('src', '') or ''
        if not actual_src or actual_src.strip() in ('', '#', 'about:blank'):
            for candidate in [img.get('data-src'), img.get('data-original'),
                              img.get('data-lazy-src')]:
                if candidate and candidate.strip() not in ('', '#', 'about:blank'):
                    actual_src = candidate
                    break

        # URL 协议修复
        if actual_src.startswith('//'):
            actual_src = 'https:' + actual_src
        elif actual_src.startswith('/') and base_url:
            actual_src = base_url + actual_src

        img['src'] = actual_src

        # alt 文本生成
        if not (img.get('alt') or '').strip():
            filename = actual_src.rsplit('/', 1)[-1]
            name_part = re.sub(r'[-_.]', ' ', filename)
            name_part = re.sub(r'\.\w{1,4}$', '', name_part).strip()
            img['alt'] = name_part if name_part and len(name_part) < 60 else '图片'
```

#### Playwright 隐身模式

```python
context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
    window.chrome = {runtime: {}};
""")
```

---

## 5. 测试情况

### 5.1 单元测试

测试框架：`unittest` + `unittest.mock`  
测试文件：`test_runner.py`  
测试样本：`test_samples/case1.html` ~ `case3.html`

| 测试类 | 测试用例 | 数量 | 说明 |
|--------|---------|------|------|
| TestHTMLToMarkdownConverter | test_validate_url_valid | 1 | 验证合法 URL |
| | test_validate_url_invalid | 1 | 验证非法 URL |
| | test_validate_html_valid | 1 | 验证合法 HTML |
| | test_validate_html_invalid | 1 | 验证非法 HTML |
| | test_convert_from_html_case1 | 1 | 中文科技新闻转换 |
| | test_convert_from_html_case2 | 1 | 英文编程教程转换 |
| | test_convert_from_html_case3 | 1 | RESTful API 指南转换（含表格） |
| | test_convert_from_html_invalid | 1 | 非法 HTML 异常处理 |
| | test_convert_from_url_invalid | 1 | 非法 URL 异常处理 |
| | test_fetch_html_from_url_success | 1 | Mock: 成功抓取 |
| | test_fetch_html_from_url_timeout | 1 | Mock: 超时处理 |
| | test_fetch_html_from_url_connection_error | 1 | Mock: 连接失败 |
| | test_fetch_html_from_url_http_error | 1 | Mock: HTTP 错误 |
| | test_save_markdown_success | 1 | 文件保存成功 |
| | test_save_markdown_empty_filename | 1 | 空文件名异常 |
| | test_save_markdown_invalid_filename | 1 | 非法文件名异常 |
| | test_save_markdown_permission_error | 1 | 权限错误（Windows 跳过） |
| TestGUILogic | test_mutual_exclusion_simulation | 1 | URL/HTML 互斥逻辑 |
| | test_sanitize_filename | 1 | 文件名清理 |
| | test_url_count_limit | 1 | URL 数量限制 |

**总计：20 个测试用例，全部通过（1 个 Windows 平台跳过）**

### 5.2 多站点兼容性测试

| 网站 | 类型 | 反爬机制 | 结果 |
|------|------|---------|------|
| mohrss.gov.cn | 政府网站 | JS Cookie 挑战 | ✅ 通过 |
| biji.com | SPA 应用 | JavaScript 动态渲染 | ✅ 通过 |
| baijiahao.baidu.com | 内容平台 | 安全验证 + User-Agent 检测 | ✅ 通过 |
| cac.gov.cn | 政府网站 | 协议相对路径图片 | ✅ 通过 |
| 新华社等常规网站 | 新闻媒体 | 无 | ✅ 通过 |

### 5.3 打包测试

| 平台 | 输出格式 | 体积 | GUI 启动 | 命令行模式 |
|------|---------|------|---------|-----------|
| Windows 11 | exe (目录) | 129.4 MB | ✅ 正常 | ✅ `--install-browsers` |
| macOS | .app + .dmg | 待构建 | 脚本就绪 | 脚本就绪 |

---

## 6. 项目文件结构

```
HtmlToMd/
├── main.py                 # 应用入口，支持 --install-browsers 参数
├── converter.py            # HTML → Markdown 核心转换引擎
├── fetcher.py              # SmartFetcher 智能爬取模块
├── gui.py                  # Tkinter GUI 界面
├── requirements.txt        # Python 依赖
├── test_runner.py          # 单元测试
├── HtmlToMd.spec           # PyInstaller 打包配置
├── build_windows.bat       # Windows 打包脚本
├── build_macos.sh          # macOS 打包脚本
├── test_samples/           # 测试样本
│   ├── case1.html          # 中文科技新闻
│   ├── case1_expected.md
│   ├── case2.html          # 英文编程教程
│   ├── case2_expected.md
│   ├── case3.html          # RESTful API 指南
│   └── case3_expected.md
├── logs/                   # 运行日志
│   └── htmltomd.log
└── dist/                   # 打包输出
    └── HtmlToMd/
        ├── HtmlToMd.exe
        ├── 安装浏览器引擎.bat
        └── _internal/      # 依赖文件
```

### 依赖清单

| 包 | 版本 | 用途 |
|----|------|------|
| requests | 2.31.0 | HTTP 请求 |
| markdownify | 0.11.6 | HTML → Markdown 转换 |
| beautifulsoup4 | 4.12.2 | HTML 解析 |
| playwright | 1.59.0 | 无头浏览器渲染 |
| pyperclip | 1.8.2 | 剪贴板操作 |

---

> 文档生成时间：2026-05-04  
> 文档版本：v1.0
