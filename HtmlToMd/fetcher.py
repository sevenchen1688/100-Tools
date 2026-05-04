import os
import re
import json
import sys
import time
import random
import logging
import subprocess
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse, urljoin
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def _is_frozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def _get_app_dir():
    if _is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).parent


def _ensure_playwright_browsers(logger=None):
    env_var = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '')
    if env_var and Path(env_var).exists():
        return True

    app_dir = _get_app_dir()
    browser_dir = app_dir / 'browsers'

    chromium_dirs = list(browser_dir.glob('chromium-*')) if browser_dir.exists() else []
    if chromium_dirs:
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browser_dir)
        if logger:
            logger.info(f"Playwright 浏览器路径: {browser_dir}")
        return True

    if logger:
        logger.info("首次运行，正在安装 Playwright 浏览器引擎 (约 200MB)...")
    try:
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browser_dir)
        result = subprocess.run(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            capture_output=True, text=True, timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        if result.returncode == 0:
            if logger:
                logger.info("Playwright 浏览器安装完成")
            return True
        else:
            if logger:
                logger.warning(f"Playwright 安装失败: {result.stderr}")
            return False
    except Exception as e:
        if logger:
            logger.warning(f"Playwright 安装异常: {e}")
        return False


UA_POOL = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
]

ACCEPT_LANGUAGES = [
    'zh-CN,zh;q=0.9,en;q=0.8',
    'zh-CN,zh;q=0.9',
    'zh-CN,zh;q=0.8,en-US;q=0.7,en;q=0.6',
    'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
]

SEC_FETCH_DEST = ['document', 'document', 'document', 'empty']
SEC_FETCH_MODE = ['navigate', 'navigate', 'no-cors']
SEC_FETCH_SITE = ['none', 'none', 'same-origin']
SEC_FETCH_USER = ['?1', '?1', '?0']


class SmartFetcher:
    def __init__(self, logger=None, timeout=20, max_retries=3, delay_range=(1.0, 3.0),
                 respect_robots=False, playwright_timeout=30000):
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay_range = delay_range
        self.respect_robots = respect_robots
        self.playwright_timeout = playwright_timeout
        self._last_request_time = 0
        self._robots_cache: Dict[str, bool] = {}

        if logger:
            self.logger = logger
        else:
            self._setup_default_logger()

    def _setup_default_logger(self):
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'htmltomd.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _build_headers(self, url: str) -> dict:
        parsed = urlparse(url)
        referer = f'{parsed.scheme}://{parsed.netloc}/'

        headers = {
            'User-Agent': random.choice(UA_POOL),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice(ACCEPT_LANGUAGES),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': random.choice(SEC_FETCH_DEST),
            'Sec-Fetch-Mode': random.choice(SEC_FETCH_MODE),
            'Sec-Fetch-Site': random.choice(SEC_FETCH_SITE),
            'Sec-Fetch-User': random.choice(SEC_FETCH_USER),
            'Referer': referer,
            'Cache-Control': 'max-age=0',
        }
        return headers

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        min_delay = random.uniform(*self.delay_range)
        if elapsed < min_delay:
            wait = min_delay - elapsed
            self.logger.debug(f"频率控制: 等待 {wait:.1f}s")
            time.sleep(wait)
        self._last_request_time = time.time()

    def _check_robots(self, url: str) -> bool:
        if not self.respect_robots:
            return True

        parsed = urlparse(url)
        robots_key = f'{parsed.scheme}://{parsed.netloc}'

        if robots_key in self._robots_cache:
            return self._robots_cache[robots_key]

        try:
            robots_url = urljoin(robots_key, '/robots.txt')
            resp = requests.get(robots_url, timeout=5, headers={'User-Agent': random.choice(UA_POOL)})
            if resp.status_code != 200:
                self._robots_cache[robots_key] = True
                return True

            lines = resp.text.split('\n')
            user_agent_match = False
            for line in lines:
                line = line.strip().lower()
                if line.startswith('user-agent:') and ('*' in line or 'bot' in line):
                    user_agent_match = True
                elif user_agent_match and line.startswith('disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path == '/' or parsed.path.startswith(path):
                        self.logger.info(f"robots.txt 禁止访问: {url}")
                        self._robots_cache[robots_key] = False
                        return False
                elif line.startswith('user-agent:'):
                    user_agent_match = False

            self._robots_cache[robots_key] = True
            return True
        except Exception:
            self._robots_cache[robots_key] = True
            return True

    def _is_js_challenge(self, html: str) -> bool:
        indicators = ['__tst_status', 'EO_Bot_Ssid', '_0x649a', '_0x49a6',
                       'acw_sc__v2', 'anti_bot', 'challenge-platform']
        match_count = sum(1 for ind in indicators if ind in html)
        return match_count >= 2 and len(html) < 5000

    def _is_spa_page(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        if not body:
            return False
        body_text = body.get_text(strip=True)
        if len(body_text) > 300:
            return False
        app_div = soup.find('div', id='app') or soup.find('div', id='root')
        if app_div:
            scripts = soup.find_all('script', src=True)
            if len(scripts) >= 1:
                return True
        return False

    def _is_security_verification(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('title')
        if not title_tag:
            return False
        title_text = title_tag.get_text(strip=True)

        keywords = ['安全验证', '安全检查', 'Just a moment', 'Attention Required',
                     'Access denied', 'Access Denied', 'Forbidden',
                     '请输入验证码', '人机验证', '滑动验证']
        for kw in keywords:
            if kw in title_text:
                body = soup.find('body')
                body_text = body.get_text(strip=True) if body else ''
                if len(body_text) < 800:
                    return True

        body_keywords = ['安全验证', '请完成安全验证', '人机验证', '滑动验证',
                          'cf-browser-verification', 'challenge-running']
        body = soup.find('body')
        if body:
            body_text = body.get_text(strip=True)
            for kw in body_keywords:
                if kw in body_text and len(body_text) < 800:
                    return True

        if '安全验证' in html and len(html) < 5000:
            return True

        return False

    def _is_captcha_page(self, html: str) -> bool:
        soup = BeautifulSoup(html, 'html.parser')
        captcha_indicators = [
            soup.find('div', id=re.compile(r'captcha|verify|check', re.I)),
            soup.find('img', attrs={'src': re.compile(r'captcha|verify|code', re.I)}),
            soup.find('div', class_=re.compile(r'captcha|verify|slider', re.I)),
        ]
        if any(indicators for indicators in captcha_indicators):
            body = soup.find('body')
            if body and len(body.get_text(strip=True)) < 800:
                return True
        return False

    def _solve_js_challenge(self, js_code: str) -> dict:
        modified_js = js_code.replace('<script>', '').replace('</script>', '')
        wrapper_js = (
            'var _cookies = [];\n'
            'var document = {\n'
            '    set cookie(val) { _cookies.push(val); },\n'
            '    get cookie() { return _cookies.join("; "); }\n'
            '};\n'
            'var setTimeout = function(fn, ms) {};\n'
            + modified_js +
            '\nconsole.log(JSON.stringify(_cookies));\n'
        )

        try:
            result = subprocess.run(
                ['node', '-e', wrapper_js],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            if result.returncode != 0:
                self.logger.warning(f"Node.js 执行 JS 验证失败: {result.stderr}")
                return {}

            cookies = {}
            for cookie_str in json.loads(result.stdout.strip()):
                parts = cookie_str.split(';')[0]
                name_val = parts.split('=', 1)
                if len(name_val) == 2:
                    cookies[name_val[0]] = name_val[1]
                    self.logger.info(f"解析验证 Cookie: {name_val[0]}={name_val[1]}")
            return cookies
        except FileNotFoundError:
            self.logger.warning("未找到 Node.js，无法解决 JS 验证。请安装: https://nodejs.org/")
            return {}
        except subprocess.TimeoutExpired:
            self.logger.warning("Node.js 执行超时")
            return {}
        except Exception as e:
            self.logger.warning(f"解决 JS 验证时出错: {str(e)}")
            return {}

    def _render_with_playwright(self, url: str, stealth=True) -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise Exception(
                "该网页需要无头浏览器渲染，但未安装 Playwright。\n"
                "请执行: pip install playwright && python -m playwright install chromium"
            )

        if _is_frozen():
            _ensure_playwright_browsers(self.logger)

        self.logger.info("使用 Playwright 无头浏览器渲染页面...")
        try:
            with sync_playwright() as p:
                launch_args = [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                ]
                browser = p.chromium.launch(headless=True, args=launch_args)

                context = browser.new_context(
                    viewport={'width': 1280 + random.randint(0, 200),
                              'height': 720 + random.randint(0, 100)},
                    user_agent=random.choice(UA_POOL),
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                    java_script_enabled=True,
                )

                if stealth:
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                        Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                        window.chrome = {runtime: {}};
                        const originalQuery = window.navigator.permissions.query;
                        window.navigator.permissions.query = (parameters) =>
                            parameters.name === 'notifications'
                                ? Promise.resolve({state: Notification.permission})
                                : originalQuery(parameters);
                    """)

                page = context.new_page()

                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                """)

                page.goto(url, wait_until='domcontentloaded', timeout=self.playwright_timeout)

                page.wait_for_timeout(random.randint(2000, 4000))

                try:
                    page.wait_for_load_state('networkidle', timeout=10000)
                except Exception:
                    pass

                page.wait_for_timeout(random.randint(1000, 2000))

                html = page.content()
                browser.close()

                self.logger.info(f"Playwright 渲染完成，内容长度: {len(html)}")
                return html
        except Exception as e:
            if 'Playwright' in str(e) or '渲染' in str(e):
                raise
            raise Exception(f"Playwright 渲染失败: {str(e)}")

    def _request_with_retry(self, session: requests.Session, url: str, headers: dict) -> requests.Response:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                self._rate_limit()
                current_headers = self._build_headers(url)
                current_headers.update(headers)

                response = session.get(url, timeout=self.timeout, headers=current_headers,
                                       allow_redirects=True)
                response.raise_for_status()
                return response
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response else 0
                if status == 429:
                    wait = (2 ** attempt) * 2 + random.uniform(0, 2)
                    self.logger.warning(f"频率限制 (429)，等待 {wait:.1f}s 后重试 ({attempt+1}/{self.max_retries})")
                    time.sleep(wait)
                    last_error = e
                elif status in (403, 503):
                    wait = (2 ** attempt) * 1.5 + random.uniform(0, 1)
                    self.logger.warning(f"访问被拒 ({status})，等待 {wait:.1f}s 后重试 ({attempt+1}/{self.max_retries})")
                    time.sleep(wait)
                    last_error = e
                else:
                    raise
            except requests.exceptions.Timeout:
                wait = (2 ** attempt) + random.uniform(0, 1)
                self.logger.warning(f"请求超时，等待 {wait:.1f}s 后重试 ({attempt+1}/{self.max_retries})")
                time.sleep(wait)
                last_error = requests.exceptions.Timeout()
            except requests.exceptions.ConnectionError as e:
                wait = (2 ** attempt) * 2 + random.uniform(0, 2)
                self.logger.warning(f"连接失败，等待 {wait:.1f}s 后重试 ({attempt+1}/{self.max_retries})")
                time.sleep(wait)
                last_error = e

        if isinstance(last_error, requests.exceptions.Timeout):
            raise Exception("网络请求超时，请检查网络连接或稍后重试")
        elif isinstance(last_error, requests.exceptions.ConnectionError):
            raise Exception("网络连接失败，请检查网络连接")
        elif isinstance(last_error, requests.exceptions.HTTPError):
            status = last_error.response.status_code if last_error.response else 0
            raise Exception(f"HTTP 错误: {status}")
        raise Exception(f"请求失败，已重试 {self.max_retries} 次")

    def fetch(self, url: str) -> str:
        if not self._check_robots(url):
            raise Exception(
                "目标网站 robots.txt 禁止爬取该页面。\n"
                "请尊重网站的爬取策略，或在浏览器中手动复制内容。"
            )

        self.logger.info(f"开始抓取网页: {url}")

        session = requests.Session()

        try:
            response = self._request_with_retry(session, url, {})
            response.encoding = response.apparent_encoding or 'utf-8'
            html = response.text
        except Exception as e:
            if any(kw in str(e) for kw in ['HTTP 错误', '超时', '连接失败', 'robots']):
                raise
            self.logger.warning(f"首次请求失败: {e}，尝试 Playwright 渲染...")
            return self._render_with_playwright(url)

        if self._is_js_challenge(html):
            self.logger.info("检测到 JS 反爬验证 (Cookie 挑战)，尝试自动解决...")
            cookies = self._solve_js_challenge(html)
            if cookies:
                for name, value in cookies.items():
                    session.cookies.set(name, value)
                self.logger.info("携带验证 Cookie 重新请求...")
                try:
                    response = self._request_with_retry(session, url, {})
                    response.encoding = response.apparent_encoding or 'utf-8'
                    if not self._is_js_challenge(response.text):
                        self.logger.info("JS 验证已通过，成功获取真实页面")
                        return response.text
                except Exception:
                    pass
            self.logger.info("JS 验证无法通过 Cookie 解决，回退到 Playwright 渲染...")
            return self._render_with_playwright(url)

        if self._is_spa_page(html):
            self.logger.info("检测到 SPA 单页应用，使用 Playwright 渲染...")
            return self._render_with_playwright(url)

        if self._is_security_verification(html):
            self.logger.info("检测到安全验证页面，使用 Playwright 渲染...")
            return self._render_with_playwright(url)

        if self._is_captcha_page(html):
            self.logger.info("检测到验证码页面，使用 Playwright 渲染...")
            return self._render_with_playwright(url)

        self.logger.info(f"网页抓取成功，编码: {response.encoding}")
        return html
