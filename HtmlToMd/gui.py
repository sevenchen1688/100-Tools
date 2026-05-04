import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from converter import HTMLToMarkdownConverter


C = {
    'bg': '#eef1f6',
    'card': '#ffffff',
    'card_alt': '#f7f8fc',
    'primary': '#5b5fe6',
    'primary_light': '#7c7ff0',
    'primary_dark': '#4849c7',
    'primary_bg': '#eef0ff',
    'accent': '#6c5ce7',
    'success': '#00b894',
    'success_bg': '#e6faf5',
    'error': '#e74c3c',
    'error_bg': '#fdecea',
    'warning': '#f39c12',
    'text': '#2d3436',
    'text_mid': '#636e72',
    'text_light': '#b2bec3',
    'border': '#dfe6e9',
    'border_light': '#f0f3f7',
    'input_bg': '#fafbfc',
    'input_focus': '#ffffff',
    'shadow': '#c8d6e5',
    'gradient_start': '#5b5fe6',
    'gradient_end': '#a29bfe',
    'divider': '#ecf0f1',
    'tag_bg': '#eef0ff',
    'tag_text': '#5b5fe6',
}

FONT = {
    'title': ('Microsoft YaHei UI', 18, 'bold'),
    'subtitle': ('Microsoft YaHei UI', 9),
    'section': ('Microsoft YaHei UI', 10, 'bold'),
    'body': ('Microsoft YaHei UI', 9),
    'hint': ('Microsoft YaHei UI', 8),
    'mono': ('Consolas', 9),
    'mono_lg': ('Consolas', 10),
    'button': ('Microsoft YaHei UI', 10, 'bold'),
    'button_sm': ('Microsoft YaHei UI', 9),
    'status': ('Microsoft YaHei UI', 9),
    'counter': ('Microsoft YaHei UI', 8, 'bold'),
}


class GradientHeader(tk.Canvas):
    def __init__(self, parent, height=80, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, **kwargs)
        self._height = height
        self.bind('<Configure>', self._draw)

    def _draw(self, event=None):
        self.delete('all')
        w = self.winfo_width()
        h = self._height
        steps = 120
        for i in range(steps):
            ratio = i / steps
            r1, g1, b1 = self._hex2rgb(C['gradient_start'])
            r2, g2, b2 = self._hex2rgb(C['gradient_end'])
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            x0 = int(w * i / steps)
            x1 = int(w * (i + 1) / steps)
            self.create_rectangle(x0, 0, x1, h, fill=color, outline='')

        self.create_text(28, h // 2 - 12, text='HTML \u2192 Markdown',
                         fill='white', font=FONT['title'], anchor='w')
        self.create_text(28, h // 2 + 16, text='\u6279\u91cf\u8f6c\u6362\u5668',
                         fill='#d5d5ff', font=('Microsoft YaHei UI', 11), anchor='w')

        self.create_text(w - 28, h // 2 - 8,
                         text='\u6279\u91cf\u94fe\u63a5 \u00b7 \u81ea\u52a8\u6807\u9898 \u00b7 \u53cd\u722c\u5904\u7406',
                         fill='#c8c8ff', font=FONT['subtitle'], anchor='e')
        self.create_text(w - 28, h // 2 + 10, text='JS Challenge \u00b7 SPA Render \u00b7 Smart Clean',
                         fill='#a8a8ee', font=('Microsoft YaHei UI', 7), anchor='e')

    @staticmethod
    def _hex2rgb(hex_color):
        h = hex_color.lstrip('#')
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


class AnimatedButton(tk.Frame):
    def __init__(self, parent, text='', command=None, style='primary', **kwargs):
        bg = C['primary'] if style == 'primary' else C['card']
        fg = 'white' if style == 'primary' else C['text']
        bd_color = C['primary'] if style == 'primary' else C['border']

        super().__init__(parent, bg=bd_color, **kwargs)
        self._command = command
        self._style = style
        self._bg = bg
        self._fg = fg

        self._btn = tk.Label(
            self, text=text, font=FONT['button'] if style == 'primary' else FONT['button_sm'],
            bg=bg, fg=fg, cursor='hand2', padx=24 if style == 'primary' else 14,
            pady=8 if style == 'primary' else 5
        )
        self._btn.pack(fill=tk.BOTH, expand=True)

        self._btn.bind('<Enter>', self._on_enter)
        self._btn.bind('<Leave>', self._on_leave)
        self._btn.bind('<ButtonPress-1>', self._on_press)
        self._btn.bind('<ButtonRelease-1>', self._on_release)

    def _on_enter(self, e):
        if self._style == 'primary':
            self._btn.config(bg=C['primary_dark'])
        else:
            self._btn.config(bg=C['border_light'])

    def _on_leave(self, e):
        self._btn.config(bg=self._bg)

    def _on_press(self, e):
        self._btn.config(bg=C['primary_dark'] if self._style == 'primary' else C['border'])

    def _on_release(self, e):
        self._btn.config(bg=self._bg)
        if self._command:
            self._command()

    def config(self, **kwargs):
        if 'state' in kwargs:
            state = kwargs.pop('state')
            if state == 'disabled':
                self._btn.config(bg='#b2bec3', fg='#dfe6e9', cursor='arrow')
                self._bg = '#b2bec3'
                self.config(bg='#b2bec3')
            else:
                self._bg = C['primary'] if self._style == 'primary' else C['card']
                self._btn.config(bg=self._bg, fg=self._fg, cursor='hand2')
                self.config(bg=C['primary'] if self._style == 'primary' else C['border'])
        if 'text' in kwargs:
            self._btn.config(text=kwargs.pop('text'))
        super().config(**kwargs)


class StatusIndicator(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=C['bg'], **kwargs)
        self._dot = tk.Canvas(self, width=8, height=8, highlightthickness=0, bg=C['bg'])
        self._dot.pack(side=tk.LEFT, padx=(0, 6))
        self._dot.create_oval(1, 1, 7, 7, fill=C['text_light'], outline='', tags='dot')

        self._label = tk.Label(self, text='\u5c31\u7eea', font=FONT['status'],
                               bg=C['bg'], fg=C['text_light'])
        self._label.pack(side=tk.LEFT)

        self._pulse_id = None

    def set_status(self, text, state='idle'):
        self._label.config(text=text)
        self._dot.delete('dot')

        colors = {
            'idle': C['text_light'],
            'working': C['warning'],
            'success': C['success'],
            'error': C['error'],
        }
        color = colors.get(state, C['text_light'])
        self._dot.create_oval(1, 1, 7, 7, fill=color, outline='', tags='dot')

        if state == 'working':
            self._pulse()
        else:
            if self._pulse_id:
                self.after_cancel(self._pulse_id)
                self._pulse_id = None

    def _pulse(self):
        try:
            current = self._dot.itemcget('dot', 'fill')
            next_color = C['warning'] if current == C['accent'] else C['accent']
            self._dot.itemconfig('dot', fill=next_color)
            self._pulse_id = self.after(500, self._pulse)
        except tk.TclError:
            pass


class SectionCard(tk.Frame):
    def __init__(self, parent, title='', hint='', icon='', **kwargs):
        super().__init__(parent, bg=C['card'], highlightthickness=1,
                         highlightbackground=C['border'], highlightcolor=C['border'],
                         **kwargs)

        header = tk.Frame(self, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 0))

        if icon:
            tk.Label(header, text=icon, font=('Segoe UI Emoji', 11),
                     bg=C['card'], fg=C['primary']).pack(side=tk.LEFT, padx=(0, 6))

        tk.Label(header, text=title, font=FONT['section'],
                 bg=C['card'], fg=C['text']).pack(side=tk.LEFT)

        if hint:
            tk.Label(header, text=hint, font=FONT['hint'],
                     bg=C['card'], fg=C['text_light']).pack(side=tk.LEFT, padx=(8, 0))


class HTMLToMarkdownGUI:
    def __init__(self, root):
        self.root = root
        self.converter = HTMLToMarkdownConverter()
        self.output_dir = ''
        self.is_converting = False
        self.setup_window()
        self.setup_styles()
        self.setup_ui()
        self.setup_bindings()

    def setup_window(self):
        self.root.title("HTML \u2192 Markdown \u6279\u91cf\u8f6c\u6362\u5668")
        self.root.geometry("920x760")
        self.root.minsize(820, 660)
        self.root.configure(bg=C['bg'])
        self.root.resizable(True, True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 920) // 2
        y = (screen_height - 760) // 2
        self.root.geometry(f"920x760+{x}+{y}")

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('TProgressbar',
                             troughcolor=C['border_light'],
                             background=C['primary'],
                             thickness=6,
                             borderwidth=0)

        self.style.map('TProgressbar',
                       background=[('active', C['primary_light'])])

    def setup_ui(self):
        self._create_header()

        content = tk.Frame(self.root, bg=C['bg'])
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self._create_url_section(content)
        self._create_html_section(content)
        self._create_output_section(content)
        self._create_action_section(content)
        self._create_progress_section(content)

    def _create_header(self):
        header = GradientHeader(self.root, height=80)
        header.pack(fill=tk.X)

        sep = tk.Frame(self.root, height=1, bg=C['primary_dark'])
        sep.pack(fill=tk.X)

    def _create_url_section(self, parent):
        card = SectionCard(parent, title='\u6279\u91cf\u94fe\u63a5\u8f93\u5165',
                           hint='\u6bcf\u884c\u4e00\u4e2a\u94fe\u63a5\uff0c\u6700\u591a10\u4e2a', icon='\U0001f517')
        card.pack(fill=tk.X, pady=(0, 10))

        self.url_text = tk.Text(
            card, height=5, wrap=tk.WORD, font=FONT['mono_lg'],
            bg=C['input_bg'], fg=C['text'], insertbackground=C['primary'],
            selectbackground=C['primary'], selectforeground='white',
            relief=tk.FLAT, borderwidth=0, highlightthickness=1,
            highlightcolor=C['primary'], highlightbackground=C['border'],
            padx=14, pady=10, undo=True, exportselection=0
        )
        self.url_text.pack(fill=tk.X, padx=16, pady=(8, 0))

        bottom = tk.Frame(card, bg=C['card'])
        bottom.pack(fill=tk.X, padx=16, pady=(4, 12))

        self.url_count_label = tk.Label(
            bottom, text='0 / 10', font=FONT['counter'],
            bg=C['tag_bg'], fg=C['tag_text'], padx=8, pady=2
        )
        self.url_count_label.pack(side=tk.RIGHT)

        tk.Label(bottom, text='\u5df2\u8f93\u5165\u94fe\u63a5\u6570', font=FONT['hint'],
                 bg=C['card'], fg=C['text_light']).pack(side=tk.RIGHT, padx=(0, 6))

    def _create_html_section(self, parent):
        card = SectionCard(parent, title='\u6216\u7c98\u8d34 HTML \u6e90\u7801',
                           hint='\u5355\u4e2a\u8f6c\u6362\u6a21\u5f0f', icon='\U0001f4dd')
        card.pack(fill=tk.X, pady=(0, 10))

        self.html_text = tk.Text(
            card, height=4, wrap=tk.WORD, font=FONT['mono'],
            bg=C['input_bg'], fg=C['text'], insertbackground=C['primary'],
            selectbackground=C['primary'], selectforeground='white',
            relief=tk.FLAT, borderwidth=0, highlightthickness=1,
            highlightcolor=C['primary'], highlightbackground=C['border'],
            padx=14, pady=10, exportselection=0
        )
        self.html_text.pack(fill=tk.X, padx=16, pady=(8, 12))

        self._html_scroll = ttk.Scrollbar(card, orient=tk.VERTICAL, command=self.html_text.yview)
        self.html_text.config(yscrollcommand=self._html_scroll.set)

    def _create_output_section(self, parent):
        card = SectionCard(parent, title='\u8f93\u51fa\u76ee\u5f55', icon='\U0001f4c1')
        card.pack(fill=tk.X, pady=(0, 10))

        row = tk.Frame(card, bg=C['card'])
        row.pack(fill=tk.X, padx=16, pady=(8, 12))

        self.dir_entry = tk.Entry(
            row, font=FONT['body'], bg=C['input_bg'], fg=C['text'],
            insertbackground=C['primary'], readonlybackground=C['input_bg'],
            relief=tk.FLAT, borderwidth=0, highlightthickness=1,
            highlightcolor=C['primary'], highlightbackground=C['border'],
            exportselection=0
        )
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=7)
        self.dir_entry.config(state='readonly')

        self.dir_button = AnimatedButton(
            row, text='\U0001f4c2 \u9009\u62e9\u76ee\u5f55', command=self.on_select_directory, style='secondary'
        )
        self.dir_button.pack(side=tk.RIGHT)

    def _create_action_section(self, parent):
        row = tk.Frame(parent, bg=C['bg'])
        row.pack(fill=tk.X, pady=(0, 10))

        self.convert_button = AnimatedButton(
            row, text='\u25b6  \u5f00\u59cb\u6279\u91cf\u8f6c\u6362', command=self.on_convert, style='primary'
        )
        self.convert_button.pack(side=tk.LEFT)

        self.status_indicator = StatusIndicator(row)
        self.status_indicator.pack(side=tk.LEFT, padx=(16, 0), fill=tk.Y)

    def _create_progress_section(self, parent):
        card = SectionCard(parent, title='\u8f6c\u6362\u8fdb\u5ea6', icon='\U0001f4ca')
        card.pack(fill=tk.BOTH, expand=True)

        progress_row = tk.Frame(card, bg=C['card'])
        progress_row.pack(fill=tk.X, padx=16, pady=(8, 4))

        self.progress_bar = ttk.Progressbar(
            progress_row, mode='determinate', length=400, style='TProgressbar'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress_label = tk.Label(
            progress_row, text='', font=FONT['hint'],
            bg=C['card'], fg=C['text_light'], width=10, anchor='e'
        )
        self.progress_label.pack(side=tk.RIGHT, padx=(8, 0))

        result_container = tk.Frame(card, bg=C['card'])
        result_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 12))

        self._result_scroll = ttk.Scrollbar(result_container, orient=tk.VERTICAL)
        self._result_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_text = tk.Text(
            result_container, height=6, wrap=tk.WORD, font=FONT['mono'],
            bg=C['card_alt'], fg=C['text'], insertbackground=C['primary'],
            selectbackground=C['primary'], selectforeground='white',
            relief=tk.FLAT, borderwidth=0, highlightthickness=0,
            padx=14, pady=10, exportselection=0,
            yscrollcommand=self._result_scroll.set,
            state=tk.DISABLED, cursor='arrow'
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._result_scroll.config(command=self.result_text.yview)

        self.result_text.tag_configure('success', foreground=C['success'],
                                       font=(FONT['mono'][0], FONT['mono'][1], 'bold'))
        self.result_text.tag_configure('error', foreground=C['error'],
                                       font=(FONT['mono'][0], FONT['mono'][1], 'bold'))
        self.result_text.tag_configure('info', foreground=C['text_mid'])
        self.result_text.tag_configure('header', foreground=C['primary'],
                                       font=(FONT['mono'][0], FONT['mono'][1], 'bold'))
        self.result_text.tag_configure('divider', foreground=C['border'],
                                       font=(FONT['mono'][0], FONT['mono'][1]))

    def setup_bindings(self):
        self.url_text.bind('<KeyRelease>', self.on_url_text_change)
        self.html_text.bind('<KeyRelease>', self.on_html_text_change)

    def on_url_text_change(self, event=None):
        urls = self._get_urls()
        count = len(urls)
        self.url_count_label.config(text=f'{count} / 10')

        if count > 0:
            self.html_text.config(state=tk.DISABLED)
        else:
            self.html_text.config(state=tk.NORMAL)

    def on_html_text_change(self, event=None):
        html_content = self.html_text.get(1.0, tk.END).strip()
        if html_content:
            self.url_text.config(state=tk.DISABLED)
        else:
            self.url_text.config(state=tk.NORMAL)

    def on_select_directory(self):
        directory = filedialog.askdirectory(title="\u9009\u62e9 Markdown \u6587\u4ef6\u8f93\u51fa\u76ee\u5f55")
        if directory:
            self.output_dir = directory
            self.dir_entry.config(state=tk.NORMAL)
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)
            self.dir_entry.config(state='readonly')

    def _get_urls(self):
        text = self.url_text.get(1.0, tk.END).strip()
        if not text:
            return []
        urls = [line.strip() for line in text.split('\n') if line.strip()]
        return urls[:10]

    def on_convert(self):
        if self.is_converting:
            return

        urls = self._get_urls()
        html_content = self.html_text.get(1.0, tk.END).strip()

        if urls:
            if not self.output_dir:
                messagebox.showwarning("\u63d0\u793a", "\u8bf7\u5148\u9009\u62e9\u8f93\u51fa\u76ee\u5f55")
                return
            if len(urls) > 10:
                messagebox.showwarning("\u63d0\u793a", "\u6700\u591a\u652f\u6301\u540c\u65f6\u8f6c\u636210\u4e2a\u94fe\u63a5")
                return
            self._start_batch_convert(urls)
        elif html_content:
            if not self.output_dir:
                messagebox.showwarning("\u63d0\u793a", "\u8bf7\u5148\u9009\u62e9\u8f93\u51fa\u76ee\u5f55")
                return
            self._convert_single_html(html_content)
        else:
            messagebox.showwarning("\u63d0\u793a", "\u8bf7\u8f93\u5165 HTML \u94fe\u63a5\u6216\u7c98\u8d34 HTML \u6e90\u7801")

    def _convert_single_html(self, html):
        self.is_converting = True
        self.convert_button.config(state='disabled')
        self.status_indicator.set_status('\u6b63\u5728\u8f6c\u6362 HTML \u6e90\u7801...', 'working')
        self._clear_results()

        def worker():
            try:
                markdown_text, title = self.converter.convert_from_html(html)
                filename = self.converter.sanitize_filename(title) if title else self.converter.generate_random_filename()
                filepath = self.converter.save_markdown(markdown_text, self.output_dir, filename)
                self.root.after(0, lambda: self._on_single_success(filepath))
            except Exception as e:
                self.root.after(0, lambda: self._on_single_error(str(e)))
            finally:
                self.root.after(0, self._on_convert_done)

        threading.Thread(target=worker, daemon=True).start()

    def _start_batch_convert(self, urls):
        self.is_converting = True
        self.convert_button.config(state='disabled')
        self.status_indicator.set_status('\u6b63\u5728\u6279\u91cf\u8f6c\u6362...', 'working')
        self._clear_results()

        self._append_result(f"\u26a1 \u5f00\u59cb\u6279\u91cf\u8f6c\u6362\uff0c\u5171 {len(urls)} \u4e2a\u94fe\u63a5\n", 'header')
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(urls)
        self.progress_label.config(text='0%')

        def worker():
            success_count = 0
            fail_count = 0

            for i, url in enumerate(urls):
                self.root.after(0, lambda u=url, idx=i: self._append_result(f"\n[{idx+1}] \u5904\u7406: {u}\n", 'info'))

                try:
                    markdown_text, title = self.converter.convert_from_url(url)
                    filename = self.converter.sanitize_filename(title) if title else self.converter.generate_random_filename()

                    base = filename
                    counter = 1
                    target_path = os.path.join(self.output_dir, f"{base}.md")
                    while os.path.exists(target_path):
                        filename = f"{base}_{counter}"
                        target_path = os.path.join(self.output_dir, f"{filename}.md")
                        counter += 1

                    filepath = self.converter.save_markdown(markdown_text, self.output_dir, filename)
                    self.root.after(0, lambda fp=filepath, t=title: self._on_item_success(fp, t))
                    success_count += 1
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self._on_item_error(err))
                    fail_count += 1

                self.root.after(0, lambda idx=i: self._update_progress(idx + 1, len(urls)))

            divider = '\u2500' * 48
            self.root.after(0, lambda: self._append_result(f"\n{divider}\n", 'divider'))

            if fail_count == 0:
                summary = f"\u2705 \u8f6c\u6362\u5b8c\u6210\uff01\u5168\u90e8\u6210\u529f: {success_count} \u4e2a\u6587\u4ef6\n"
                self.root.after(0, lambda: self._append_result(summary, 'success'))
                self.root.after(0, lambda: self.status_indicator.set_status(
                    f'\u8f6c\u6362\u5b8c\u6210 \u2014 \u5168\u90e8\u6210\u529f: {success_count}', 'success'))
            else:
                summary = f"\u26a0\ufe0f \u8f6c\u6362\u5b8c\u6210 \u2014 \u6210\u529f: {success_count}  \u5931\u8d25: {fail_count}\n"
                self.root.after(0, lambda: self._append_result(summary, 'error'))
                self.root.after(0, lambda: self.status_indicator.set_status(
                    f'\u8f6c\u6362\u5b8c\u6210 \u2014 \u6210\u529f: {success_count} \u5931\u8d25: {fail_count}', 'error'))

            self.root.after(0, self._on_convert_done)

        threading.Thread(target=worker, daemon=True).start()

    def _on_single_success(self, filepath):
        self._append_result(f"\u2705 \u8f6c\u6362\u6210\u529f\uff01\n   \u4fdd\u5b58\u81f3: {filepath}\n", 'success')
        self.status_indicator.set_status('\u8f6c\u6362\u6210\u529f', 'success')

    def _on_single_error(self, error):
        self._append_result(f"\u274c \u8f6c\u6362\u5931\u8d25: {error}\n", 'error')
        self.status_indicator.set_status('\u8f6c\u6362\u5931\u8d25', 'error')

    def _on_item_success(self, filepath, title):
        display_title = title if title else os.path.basename(filepath)
        self._append_result(f"  \u2705 {display_title}\n     \u2192 {filepath}\n", 'success')

    def _on_item_error(self, error):
        self._append_result(f"  \u274c \u5931\u8d25: {error}\n", 'error')

    def _update_progress(self, current, total):
        self.progress_bar['value'] = current
        pct = int(current / total * 100) if total > 0 else 0
        self.progress_label.config(text=f'{pct}%')

    def _on_convert_done(self):
        self.is_converting = False
        self.convert_button.config(state='normal')

    def _clear_results(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.progress_label.config(text='')

    def _append_result(self, text, tag='info'):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, text, tag)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)
