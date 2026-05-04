import os
import sys
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from converter import HTMLToMarkdownConverter


class TestHTMLToMarkdownConverter(unittest.TestCase):
    def setUp(self):
        self.converter = HTMLToMarkdownConverter()
        self.test_dir = Path(__file__).parent / 'test_samples'

    def test_validate_url_valid(self):
        valid_urls = [
            'http://example.com',
            'https://example.com',
            'https://www.example.com/path',
            'http://localhost:8000'
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.converter.validate_url(url))

    def test_validate_url_invalid(self):
        invalid_urls = [
            'ftp://example.com',
            'example.com',
            'www.example.com',
            '',
            'javascript:void(0)'
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.converter.validate_url(url))

    def test_validate_html_valid(self):
        valid_html = [
            '<html></html>',
            '<HTML></HTML>',
            '<html><body>content</body></html>',
            '<!DOCTYPE html><html><head></head><body></body></html>'
        ]
        for html in valid_html:
            with self.subTest(html=html[:20]):
                self.assertTrue(self.converter.validate_html(html))

    def test_validate_html_invalid(self):
        invalid_html = [
            '<body></body>',
            '<div>content</div>',
            'plain text',
            ''
        ]
        for html in invalid_html:
            with self.subTest(html=html[:20]):
                self.assertFalse(self.converter.validate_html(html))

    def test_convert_from_html_case1(self):
        html_file = self.test_dir / 'case1.html'
        expected_file = self.test_dir / 'case1_expected.md'
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = f.read()
        
        result, title = self.converter.convert_from_html(html)
        self.assertEqual(result, expected)

    def test_convert_from_html_case2(self):
        html_file = self.test_dir / 'case2.html'
        expected_file = self.test_dir / 'case2_expected.md'
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = f.read()
        
        result, title = self.converter.convert_from_html(html)
        self.assertEqual(result, expected)

    def test_convert_from_html_case3(self):
        html_file = self.test_dir / 'case3.html'
        expected_file = self.test_dir / 'case3_expected.md'
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = f.read()
        
        result, title = self.converter.convert_from_html(html)
        self.assertEqual(result, expected)

    def test_convert_from_html_invalid(self):
        invalid_html = '<body>content</body>'
        with self.assertRaises(Exception) as context:
            self.converter.convert_from_html(invalid_html)
        self.assertIn('HTML 源码格式不正确', str(context.exception))

    def test_convert_from_url_invalid(self):
        invalid_url = 'ftp://example.com'
        with self.assertRaises(Exception) as context:
            self.converter.convert_from_url(invalid_url)
        self.assertIn('URL 格式不正确', str(context.exception))

    @patch('fetcher.SmartFetcher.fetch')
    def test_fetch_html_from_url_success(self, mock_fetch):
        mock_fetch.return_value = '<html><body>test</body></html>'

        result = self.converter.fetch_html_from_url('https://example.com')
        self.assertEqual(result, '<html><body>test</body></html>')

    @patch('fetcher.SmartFetcher.fetch')
    def test_fetch_html_from_url_timeout(self, mock_fetch):
        mock_fetch.side_effect = Exception('网络请求超时，请检查网络连接或稍后重试')

        with self.assertRaises(Exception) as context:
            self.converter.fetch_html_from_url('https://example.com')
        self.assertIn('网络请求超时', str(context.exception))

    @patch('fetcher.SmartFetcher.fetch')
    def test_fetch_html_from_url_connection_error(self, mock_fetch):
        mock_fetch.side_effect = Exception('网络连接失败，请检查网络连接')

        with self.assertRaises(Exception) as context:
            self.converter.fetch_html_from_url('https://example.com')
        self.assertIn('网络连接失败', str(context.exception))

    @patch('fetcher.SmartFetcher.fetch')
    def test_fetch_html_from_url_http_error(self, mock_fetch):
        mock_fetch.side_effect = Exception('HTTP 错误: 404')

        with self.assertRaises(Exception) as context:
            self.converter.fetch_html_from_url('https://example.com')
        self.assertIn('HTTP 错误', str(context.exception))

    def test_save_markdown_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_text = '# Test\n\nThis is a test.'
            filepath = self.converter.save_markdown(markdown_text, temp_dir, 'test_file')
            
            self.assertTrue(os.path.exists(filepath))
            self.assertTrue(filepath.endswith('.md'))
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertEqual(content, markdown_text)

    def test_save_markdown_empty_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_text = '# Test'
            with self.assertRaises(Exception) as context:
                self.converter.save_markdown(markdown_text, temp_dir, '')
            self.assertIn('文件名不能为空', str(context.exception))

    def test_save_markdown_invalid_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_text = '# Test'
            invalid_filenames = ['test/file', 'test:file', 'test*file', 'test?file', 'test<file>', 'test|file']
            
            for filename in invalid_filenames:
                with self.subTest(filename=filename):
                    with self.assertRaises(Exception) as context:
                        self.converter.save_markdown(markdown_text, temp_dir, filename)
                    self.assertIn('文件名包含非法字符', str(context.exception))

    @unittest.skipIf(os.name == 'nt', '权限测试在 Windows 上不可靠')
    def test_save_markdown_permission_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_text = '# Test'
            readonly_dir = Path(temp_dir) / 'readonly'
            readonly_dir.mkdir()
            
            os.chmod(readonly_dir, 0o444)
            
            try:
                with self.assertRaises(Exception) as context:
                    self.converter.save_markdown(markdown_text, str(readonly_dir), 'test')
                self.assertIn('没有写入权限', str(context.exception))
            finally:
                os.chmod(readonly_dir, 0o755)


class TestGUILogic(unittest.TestCase):
    def test_mutual_exclusion_simulation(self):
        import tkinter as tk
        from gui import HTMLToMarkdownGUI

        root = tk.Tk()
        root.withdraw()

        app = HTMLToMarkdownGUI(root)

        app.url_text.insert(tk.END, 'https://example.com')
        app.on_url_text_change(None)
        root.update()

        self.assertEqual(str(app.html_text['state']), 'disabled')

        app.url_text.delete(1.0, tk.END)
        app.on_url_text_change(None)
        root.update()

        self.assertEqual(str(app.html_text['state']), 'normal')

        app.html_text.insert(tk.END, '<html></html>')
        app.on_html_text_change(None)
        root.update()

        self.assertEqual(str(app.url_text['state']), 'disabled')

        app.html_text.delete(1.0, tk.END)
        app.on_html_text_change(None)
        root.update()

        self.assertEqual(str(app.url_text['state']), 'normal')

        root.destroy()

    def test_sanitize_filename(self):
        from converter import HTMLToMarkdownConverter

        self.assertEqual(HTMLToMarkdownConverter.sanitize_filename('Hello World'), 'Hello_World')
        self.assertEqual(HTMLToMarkdownConverter.sanitize_filename('Test/File:Name'), 'TestFileName')

        empty_result = HTMLToMarkdownConverter.sanitize_filename('')
        self.assertEqual(len(empty_result), 12)
        self.assertTrue(empty_result.isalnum())

        random_name = HTMLToMarkdownConverter.generate_random_filename()
        self.assertEqual(len(random_name), 12)
        self.assertTrue(random_name.isalnum())

    def test_url_count_limit(self):
        import tkinter as tk
        from gui import HTMLToMarkdownGUI

        root = tk.Tk()
        root.withdraw()

        app = HTMLToMarkdownGUI(root)

        urls = '\n'.join([f'https://example{i}.com' for i in range(12)])
        app.url_text.insert(tk.END, urls)
        app.on_url_text_change(None)
        root.update()

        self.assertEqual(app._get_urls(), [f'https://example{i}.com' for i in range(10)])
        self.assertIn('10', app.url_count_label.cget('text'))

        root.destroy()


def run_all_tests():
    print("=" * 60)
    print("HTML → Markdown 转换器测试套件")
    print("=" * 60)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestHTMLToMarkdownConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestGUILogic))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✓ 所有测试通过！")
        return 0
    else:
        print("✗ 部分测试失败，请检查错误信息")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
