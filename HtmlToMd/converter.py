import os
import re
import json
import logging
import subprocess
import requests
import markdownify
import random
import string
from typing import Optional, Tuple, List
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from fetcher import SmartFetcher


class HTMLToMarkdownConverter:
    def __init__(self):
        self.setup_logging()
        self.fetcher = SmartFetcher(logger=self.logger)

    def setup_logging(self):
        log_dir = Path(__file__).parent / 'logs'
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / 'htmltomd.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_url(self, url: str) -> bool:
        pattern = r'^https?://'
        return bool(re.match(pattern, url))

    def validate_html(self, html: str) -> bool:
        html_lower = html.lower()
        return '<html' in html_lower and '</html>' in html_lower

    def fetch_html_from_url(self, url: str) -> str:
        try:
            return self.fetcher.fetch(url)
        except Exception as e:
            error_msg = str(e)
            self.logger.error(error_msg)
            raise Exception(error_msg)

    def _extract_title(self, soup) -> str:
        title_tag = soup.find('meta', attrs={'name': 'ArticleTitle'})
        if title_tag and title_tag.get('content'):
            return title_tag['content'].strip()

        title_tag = soup.find('meta', attrs={'property': 'og:title'})
        if title_tag and title_tag.get('content'):
            return title_tag['content'].strip()

        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            for sep in ['_', '-', '|', '——']:
                if sep in title_text:
                    title_text = title_text.split(sep)[0].strip()
            return title_text

        return ''

    _JUNK_IMG_PATTERNS = [
        re.compile(r'logo|icon|banner|bg|background|arrow|btn|button|search|fold|qr|ewm|conac|computer|spinner|loading|pixel|spacer|blank|transparent|tracking|beacon|stat|analytics|share|wechat|weibo|qq|sina', re.I),
    ]
    _MIN_CONTENT_IMG_SIZE = 50

    def _is_junk_image(self, img_tag) -> bool:
        src = img_tag.get('src', '') or ''
        class_list = img_tag.get('class', []) or []
        class_str = ' '.join(class_list) if isinstance(class_list, list) else str(class_list)
        parent = img_tag.parent
        parent_class = ''
        if parent:
            pc = parent.get('class', []) or []
            parent_class = ' '.join(pc) if isinstance(pc, list) else str(pc)

        for pattern in self._JUNK_IMG_PATTERNS:
            if pattern.search(src) or pattern.search(class_str) or pattern.search(parent_class):
                return True

        width = img_tag.get('width', '')
        height = img_tag.get('height', '')
        try:
            if width and int(str(width).replace('px', '')) < self._MIN_CONTENT_IMG_SIZE:
                return True
            if height and int(str(height).replace('px', '')) < self._MIN_CONTENT_IMG_SIZE:
                return True
        except (ValueError, TypeError):
            pass

        return False

    def _process_images(self, content_element, source_url: str = ''):
        if source_url:
            parsed = urlparse(source_url)
            base_url = f'{parsed.scheme}://{parsed.netloc}'
        else:
            base_url = ''

        for img in content_element.find_all('img'):
            if self._is_junk_image(img):
                img.decompose()
                continue

            src = img.get('src', '') or ''
            data_src = img.get('data-src', '') or ''
            data_original = img.get('data-original', '') or ''
            data_lazy_src = img.get('data-lazy-src', '') or ''

            actual_src = src
            if not actual_src or actual_src.strip() in ('', '#', 'about:blank'):
                for candidate in [data_src, data_original, data_lazy_src]:
                    if candidate and candidate.strip() not in ('', '#', 'about:blank'):
                        actual_src = candidate
                        break

            if actual_src.startswith('//'):
                actual_src = 'https:' + actual_src
            elif actual_src.startswith('/') and base_url:
                actual_src = base_url + actual_src
            elif not actual_src.startswith(('http://', 'https://', 'data:')) and base_url:
                actual_src = urljoin(source_url, actual_src)

            img['src'] = actual_src

            for attr in ['data-src', 'data-original', 'data-lazy-src', 'srcset', 'loading']:
                if img.has_attr(attr):
                    del img[attr]

            alt = img.get('alt', '') or ''
            if not alt.strip():
                if actual_src:
                    filename = actual_src.rsplit('/', 1)[-1] if '/' in actual_src else actual_src
                    filename = re.sub(r'[?#].*$', '', filename)
                    name_part = re.sub(r'[-_.]', ' ', filename)
                    name_part = re.sub(r'\.\w{1,4}$', '', name_part).strip()
                    if name_part and len(name_part) < 60:
                        img['alt'] = name_part
                    else:
                        img['alt'] = '图片'
                else:
                    img['alt'] = '图片'

    def _clean_html(self, html: str, source_url: str = '') -> str:
        soup = BeautifulSoup(html, 'html.parser')

        title = self._extract_title(soup)

        for tag in soup.find_all(['script', 'style', 'iframe', 'noscript']):
            tag.decompose()

        for tag in soup.find_all(['nav', 'header', 'footer']):
            tag.decompose()

        content_selectors = [
            {'id': re.compile(r'content|article|main|post|body|text', re.I)},
            {'class_': re.compile(r'content|article|main|post|body|text|editor', re.I)},
        ]

        content_element = None
        for selector in content_selectors:
            found = soup.find('div', **selector)
            if found and len(found.get_text(strip=True)) > 100:
                content_element = found
                self.logger.info(f"找到内容区域: {selector}")
                break

        if content_element is None:
            body = soup.find('body')
            if body:
                content_element = body
            else:
                content_element = soup

        for tag in content_element.find_all(['script', 'style', 'iframe', 'noscript', 'nav', 'header', 'footer']):
            tag.decompose()

        for tag in content_element.find_all(['button', 'input', 'select', 'textarea']):
            tag.decompose()

        for tag in content_element.find_all(True, attrs={'class': re.compile(r'share|toolbar|action|btn|nav|sidebar|comment|footer|header', re.I)}):
            tag.decompose()

        self._process_images(content_element, source_url)

        content_html = str(content_element)

        if title:
            first_heading = content_element.find(['h1', 'h2', 'h3'])
            if first_heading and title in first_heading.get_text():
                pass
            else:
                title_line = f'# {title}\n\n'
                content_html = title_line + content_html

        return content_html

    def convert_to_markdown(self, html: str, source_url: str = '') -> str:
        try:
            self.logger.info("开始转换 HTML 到 Markdown")

            cleaned_html = self._clean_html(html, source_url=source_url)

            markdown_text = markdownify.markdownify(
                cleaned_html,
                heading_style="ATX",
                strip=['script', 'style']
            )

            markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
            markdown_text = markdown_text.strip()
            self.logger.info("HTML 到 Markdown 转换完成")
            return markdown_text
        except Exception as e:
            error_msg = f"转换 HTML 到 Markdown 时发生错误: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

    def save_markdown(self, markdown_text: str, directory: str, filename: str) -> str:
        try:
            if not filename:
                raise Exception("文件名不能为空")

            invalid_chars = r'[/\\:*?"<>|]'
            if re.search(invalid_chars, filename):
                raise Exception(f"文件名包含非法字符: {invalid_chars}")

            filepath = Path(directory) / f"{filename}.md"

            self.logger.info(f"开始保存文件: {filepath}")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_text)

            self.logger.info(f"文件保存成功: {filepath}")
            return str(filepath)
        except PermissionError:
            error_msg = "没有写入权限，请检查目录是否为只读"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            if "文件名" in str(e):
                raise
            error_msg = f"保存文件时发生错误: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)

    def convert_from_url(self, url: str) -> Tuple[str, str]:
        if not self.validate_url(url):
            raise Exception("URL 格式不正确，必须以 http:// 或 https:// 开头")

        html = self.fetch_html_from_url(url)
        title = self._extract_title_from_html(html)
        markdown_text = self.convert_to_markdown(html, source_url=url)
        return markdown_text, title

    def convert_from_html(self, html: str, source_url: str = '') -> Tuple[str, str]:
        if not self.validate_html(html):
            raise Exception("HTML 源码格式不正确，必须包含 <html> 和 </html> 标签")

        title = self._extract_title_from_html(html)
        markdown_text = self.convert_to_markdown(html, source_url=source_url)
        return markdown_text, title

    def _extract_title_from_html(self, html: str) -> str:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            return self._extract_title(soup)
        except Exception:
            return ''

    @staticmethod
    def generate_random_filename() -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=12))

    @staticmethod
    def sanitize_filename(title: str) -> str:
        title = re.sub(r'[/\\:*?"<>|]', '', title)
        title = re.sub(r'\s+', '_', title.strip())
        title = title[:80]
        title = title.strip('_')
        if not title:
            return HTMLToMarkdownConverter.generate_random_filename()
        return title
