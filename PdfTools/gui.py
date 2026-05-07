import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from pdf_operations import PDFOperations


C = {
    'bg': '#ecf0f1',
    'card': '#ffffff',
    'card_alt': '#f7f8fc',
    'primary': '#e74c3c',
    'primary_light': '#fdedec',
    'primary_dark': '#c0392b',
    'primary_bg': '#fef5f5',
    'accent': '#d63031',
    'success': '#27ae60',
    'success_bg': '#e8f8ef',
    'error': '#e74c3c',
    'error_bg': '#fdecea',
    'warning': '#f39c12',
    'text': '#2d3436',
    'text_mid': '#636e72',
    'text_light': '#b2bec3',
    'border': '#dfe6e9',
    'border_light': '#f0f3f7',
    'input_bg': '#fafbfc',
    'shadow': '#c8d6e5',
    'gradient_start': '#e74c3c',
    'gradient_end': '#c0392b',
    'divider': '#ecf0f1',
    'tag_bg': '#fdedec',
    'tag_text': '#e74c3c',
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

FUNCTIONS = [
    {'id': 'pdf_to_images', 'name': 'PDF转图片', 'icon': '🖼️', 
     'desc': '将PDF页面转换为图片'},
    {'id': 'images_to_pdf', 'name': '图片转PDF', 'icon': '📄',
     'desc': '将多张图片合并为PDF'},
    {'id': 'pdf_to_word', 'name': 'PDF转Word', 'icon': '📝',
     'desc': '将PDF转换为Word文档'},
    {'id': 'remove_watermark', 'name': '去除水印', 'icon': '🚫',
     'desc': '智能去除PDF水印'},
    {'id': 'add_watermark', 'name': '添加水印', 'icon': '💧',
     'desc': '为PDF添加水印'},
    {'id': 'merge_pdfs', 'name': '合并PDF', 'icon': '📚',
     'desc': '将多个PDF合并为一个'},
    {'id': 'split_pdf', 'name': '拆分PDF', 'icon': '✂️',
     'desc': '按页面拆分PDF'},
    {'id': 'rotate_pdf', 'name': '旋转PDF', 'icon': '🔄',
     'desc': '旋转PDF页面'},
    {'id': 'compress_pdf', 'name': '压缩PDF', 'icon': '📦',
     'desc': '压缩PDF文件大小'},
    {'id': 'encrypt_pdf', 'name': '加密PDF', 'icon': '🔒',
     'desc': '为PDF添加密码'},
    {'id': 'decrypt_pdf', 'name': '解密PDF', 'icon': '🔓',
     'desc': '移除PDF密码'},
    {'id': 'extract_pages', 'name': '提取页面', 'icon': '📑',
     'desc': '提取指定页面'},
    {'id': 'delete_pages', 'name': '删除页面', 'icon': '🗑️',
     'desc': '删除指定页面'},
    {'id': 'extract_text', 'name': '提取文本', 'icon': '📃',
     'desc': '提取PDF文本内容'},
    {'id': 'extract_images', 'name': '提取图片', 'icon': '🖼️',
     'desc': '提取PDF中的图片'},
]


class GradientHeader(tk.Canvas):
    def __init__(self, parent, height=80, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, **kwargs)
        self._height = height
        self.bind('<Configure>', self._draw)

    def _draw(self, event=None):
        self.delete('all')
        w = self.winfo_width()
        h = self._height
        steps = 100
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

        self.create_text(28, h // 2 - 10, text='PDF Toolkit - 全功能PDF处理工具',
                         fill='white', font=FONT['title'], anchor='w')
        self.create_text(28, h // 2 + 18, text='免费 · 安全 · 高效',
                         fill='#ffd5d2', font=('Microsoft YaHei UI', 11), anchor='w')

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

        self._label = tk.Label(self, text='就绪', font=FONT['status'],
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


class FunctionCard(tk.Frame):
    def __init__(self, parent, func_info, command=None, **kwargs):
        super().__init__(parent, bg=C['card'], highlightthickness=1,
                         highlightbackground=C['border'], highlightcolor=C['border'],
                         cursor='hand2', **kwargs)
        
        self.func_info = func_info
        self.command = command
        
        icon_label = tk.Label(self, text=func_info['icon'], font=('Segoe UI Emoji', 20),
                              bg=C['card'], fg=C['primary'])
        icon_label.pack(pady=(12, 4))
        
        name_label = tk.Label(self, text=func_info['name'], font=FONT['section'],
                              bg=C['card'], fg=C['text'])
        name_label.pack()
        
        desc_label = tk.Label(self, text=func_info['desc'], font=FONT['hint'],
                              bg=C['card'], fg=C['text_light'])
        desc_label.pack(pady=(0, 8))
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<ButtonPress-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_enter(self, e):
        self.config(highlightbackground=C['primary'], highlightcolor=C['primary'])
        self.config(bg=C['primary_bg'])
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=C['primary_bg'])

    def _on_leave(self, e):
        self.config(highlightbackground=C['border'], highlightcolor=C['border'])
        self.config(bg=C['card'])
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=C['card'])

    def _on_press(self, e):
        self.config(bg=C['primary_light'])
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=C['primary_light'])
        if self.command:
            self.command(self.func_info)

    def _on_release(self, e):
        self.config(bg=C['card'])
        for child in self.winfo_children():
            if isinstance(child, tk.Label):
                child.config(bg=C['card'])
        if self.command:
            self.command(self.func_info)


class PDFToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.pdf_ops = PDFOperations()
        self.current_function = None
        self.file_list = []
        self.output_dir = ''
        self.is_processing = False
        self.options = {}
        
        self.setup_window()
        self.setup_styles()
        self.setup_ui()
        self.setup_bindings()
        
        self.pdf_ops.set_progress_callback(self.on_progress_update)

    def setup_window(self):
        self.root.title("PDF Toolkit - 全功能PDF处理工具")
        self.root.geometry("1100x800")
        self.root.minsize(900, 700)
        self.root.configure(bg=C['bg'])
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 1100) // 2
        y = (screen_height - 800) // 2
        self.root.geometry(f"1100x800+{x}+{y}")

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
        
        main_container = tk.Frame(self.root, bg=C['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        left_panel = tk.Frame(main_container, bg=C['bg'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        
        self._create_function_grid(left_panel)
        
        right_panel = tk.Frame(main_container, bg=C['bg'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self._create_file_section(right_panel)
        self._create_options_section(right_panel)
        self._create_action_section(right_panel)
        self._create_progress_section(right_panel)
        self._create_log_section(right_panel)

    def _create_header(self):
        header = GradientHeader(self.root, height=80)
        header.pack(fill=tk.X)
        
        sep = tk.Frame(self.root, height=2, bg=C['primary_dark'])
        sep.pack(fill=tk.X)

    def _create_function_grid(self, parent):
        title = tk.Label(parent, text='📋 功能列表', font=FONT['section'],
                         bg=C['bg'], fg=C['text'])
        title.pack(anchor='w', pady=(0, 12))
        
        scroll_frame = tk.Frame(parent, bg=C['bg'])
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame, bg=C['bg'], highlightthickness=0,
                          width=260)
        scrollbar = ttk.Scrollbar(scroll_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        self.func_container = tk.Frame(canvas, bg=C['bg'])
        canvas.create_window((0, 0), window=self.func_container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        for i, func in enumerate(FUNCTIONS):
            row = i // 2
            col = i % 2
            
            card = FunctionCard(
                self.func_container,
                func,
                command=self.on_function_select
            )
            card.grid(row=row, column=col, padx=6, pady=6, sticky='nsew')
        
        self.func_container.update_idletasks()
        canvas.config(scrollregion=canvas.bbox('all'))

    def _create_file_section(self, parent):
        card = tk.Frame(parent, bg=C['card'], highlightthickness=1,
                        highlightbackground=C['border'], highlightcolor=C['border'])
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        header = tk.Frame(card, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 0))
        
        tk.Label(header, text='📁 文件列表', font=FONT['section'],
                 bg=C['card'], fg=C['text']).pack(side=tk.LEFT)
        
        tk.Label(header, text='支持拖拽添加', font=FONT['hint'],
                 bg=C['card'], fg=C['text_light']).pack(side=tk.RIGHT)
        
        drop_frame = tk.Frame(card, bg=C['primary_bg'], height=120)
        drop_frame.pack(fill=tk.X, padx=16, pady=(8, 0))
        drop_frame.pack_propagate(False)
        
        self.drop_label = tk.Label(
            drop_frame,
            text='拖拽 PDF 文件到此处\n或点击选择文件',
            font=FONT['body'],
            bg=C['primary_bg'],
            fg=C['text_mid'],
            justify='center'
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)
        
        list_frame = tk.Frame(card, bg=C['card'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)
        
        scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scroll_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.file_listbox = tk.Listbox(
            list_frame,
            font=FONT['mono'],
            bg=C['input_bg'],
            fg=C['text'],
            selectbackground=C['primary'],
            selectforeground='white',
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            height=4
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.file_listbox.yview)
        scroll_x.config(command=self.file_listbox.xview)
        
        btn_frame = tk.Frame(card, bg=C['card'])
        btn_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        
        tk.Button(btn_frame, text='添加文件', command=self.add_files,
                  font=FONT['button_sm'], bg=C['primary_bg'], fg=C['primary'],
                  relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT)
        
        tk.Button(btn_frame, text='清除列表', command=self.clear_files,
                  font=FONT['button_sm'], bg=C['bg'], fg=C['text_mid'],
                  relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT, padx=(8, 0))
        
        tk.Button(btn_frame, text='移除选中', command=self.remove_selected,
                  font=FONT['button_sm'], bg=C['bg'], fg=C['text_mid'],
                  relief=tk.FLAT, padx=12, pady=4).pack(side=tk.LEFT, padx=(8, 0))

    def _create_options_section(self, parent):
        self.options_card = tk.Frame(parent, bg=C['card'], highlightthickness=1,
                                     highlightbackground=C['border'], highlightcolor=C['border'])
        self.options_card.pack(fill=tk.X, pady=(0, 10))
        
        header = tk.Frame(self.options_card, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 8))
        
        self.options_title = tk.Label(header, text='⚙️ 选项设置', font=FONT['section'],
                                      bg=C['card'], fg=C['text'])
        self.options_title.pack(side=tk.LEFT)
        
        self.options_frame = tk.Frame(self.options_card, bg=C['card'])
        self.options_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

    def _create_action_section(self, parent):
        action_frame = tk.Frame(parent, bg=C['bg'])
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.start_button = AnimatedButton(
            action_frame,
            text='▶ 开始处理',
            command=self.start_process,
            style='primary'
        )
        self.start_button.pack(side=tk.LEFT)
        
        self.status_indicator = StatusIndicator(action_frame)
        self.status_indicator.pack(side=tk.LEFT, padx=(16, 0))
        
        output_frame = tk.Frame(action_frame, bg=C['bg'])
        output_frame.pack(side=tk.RIGHT)
        
        tk.Label(output_frame, text='输出目录:', font=FONT['hint'],
                 bg=C['bg'], fg=C['text_mid']).pack(side=tk.LEFT, padx=(0, 8))
        
        self.output_entry = tk.Entry(
            output_frame,
            font=FONT['mono'],
            width=30,
            bg=C['input_bg'],
            fg=C['text'],
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=0
        )
        self.output_entry.pack(side=tk.LEFT, padx=(0, 8))
        
        tk.Button(
            output_frame,
            text='浏览...',
            command=self.select_output_dir,
            font=FONT['button_sm'],
            bg=C['card'],
            fg=C['text'],
            relief=tk.FLAT,
            padx=12,
            pady=4
        ).pack(side=tk.LEFT)

    def _create_progress_section(self, parent):
        card = tk.Frame(parent, bg=C['card'], highlightthickness=1,
                        highlightbackground=C['border'], highlightcolor=C['border'])
        card.pack(fill=tk.X, pady=(0, 10))
        
        header = tk.Frame(card, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 8))
        
        tk.Label(header, text='📊 处理进度', font=FONT['section'],
                 bg=C['card'], fg=C['text']).pack(side=tk.LEFT)
        
        progress_frame = tk.Frame(card, bg=C['card'])
        progress_frame.pack(fill=tk.X, padx=16, pady=(0, 12))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=200,
            style='TProgressbar'
        )
        self.progress_bar.pack(fill=tk.X, expand=True)
        
        self.progress_label = tk.Label(
            progress_frame,
            text='',
            font=FONT['hint'],
            bg=C['card'],
            fg=C['text_light']
        )
        self.progress_label.pack(pady=(4, 0))

    def _create_log_section(self, parent):
        card = tk.Frame(parent, bg=C['card'], highlightthickness=1,
                        highlightbackground=C['border'], highlightcolor=C['border'])
        card.pack(fill=tk.BOTH, expand=True)
        
        header = tk.Frame(card, bg=C['card'])
        header.pack(fill=tk.X, padx=16, pady=(12, 8))
        
        tk.Label(header, text='📝 操作日志', font=FONT['section'],
                 bg=C['card'], fg=C['text']).pack(side=tk.LEFT)
        
        tk.Button(
            header,
            text='清空日志',
            command=self.clear_log,
            font=FONT['hint'],
            bg=C['bg'],
            fg=C['text_mid'],
            relief=tk.FLAT,
            padx=8,
            pady=2
        ).pack(side=tk.RIGHT)
        
        log_frame = tk.Frame(card, bg=C['card'])
        log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))
        
        scroll_y = ttk.Scrollbar(log_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            log_frame,
            font=FONT['mono'],
            bg=C['card_alt'],
            fg=C['text_mid'],
            relief=tk.FLAT,
            borderwidth=0,
            height=6,
            yscrollcommand=scroll_y.set
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.log_text.yview)
        
        self.log_text.tag_configure('success', foreground=C['success'])
        self.log_text.tag_configure('error', foreground=C['error'])
        self.log_text.tag_configure('info', foreground=C['text_mid'])
        self.log_text.tag_configure('warning', foreground=C['warning'])

    def setup_bindings(self):
        self.root.drop_target_register('DND_Files')
        self.root.dnd_bind('<<Drop>>', self.on_file_drop)

    def on_file_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        for file in files:
            if file.lower().endswith('.pdf'):
                self.add_file(file)

    def on_function_select(self, func_info):
        self.current_function = func_info['id']
        self.log(f"已选择功能: {func_info['name']}")
        self.update_options()

    def update_options(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.options = {}
        
        if not self.current_function:
            tk.Label(
                self.options_frame,
                text='请从左侧选择要使用的功能',
                font=FONT['body'],
                bg=C['card'],
                fg=C['text_light']
            ).pack(anchor='w')
            return
        
        func_id = self.current_function
        
        if func_id == 'pdf_to_images':
            self._add_option('format', '图片格式:', 'radio',
                            values=[('PNG', 'png'), ('JPG', 'jpg')])
            self._add_option('dpi', '图片质量 (DPI):', 'entry', default='150')
            self._add_option('pages', '页面范围:', 'entry', default='全部')
            
        elif func_id == 'images_to_pdf':
            self._add_option('quality', 'PDF质量:', 'radio',
                            values=[('高质量', 'high'), ('中等质量', 'medium'), ('低质量(小文件)', 'low')])
            
        elif func_id == 'pdf_to_word':
            self._add_option('pages', '页面范围:', 'entry', default='全部')
            
        elif func_id == 'remove_watermark':
            self._add_option('type', '水印类型:', 'radio',
                            values=[('自动识别', 'auto'), ('文字水印', 'text'), ('图片水印', 'image')])
            
        elif func_id == 'add_watermark':
            self._add_option('watermark_type', '水印类型:', 'radio',
                            values=[('文字水印', 'text'), ('图片水印', 'image')])
            self._add_option('text', '水印文字:', 'entry', default='WATERMARK')
            self._add_option('opacity', '透明度:', 'scale', range=(0.1, 0.9))
            self._add_option('position', '位置:', 'radio',
                            values=[('居中', 'center'), ('顶部', 'top'), ('底部', 'bottom'), ('对角线', 'diagonal')])
            
        elif func_id == 'split_pdf':
            self._add_option('split_mode', '拆分方式:', 'radio',
                            values=[('按范围', 'ranges'), ('每N页', 'every'), ('逐页拆分', 'single')])
            self._add_option('ranges', '页面范围:', 'entry', default='1-3, 5-7')
            self._add_option('pages_per_split', '每页数:', 'entry', default='1')
            
        elif func_id == 'rotate_pdf':
            self._add_option('rotation', '旋转角度:', 'radio',
                            values=[('90°', 90), ('180°', 180), ('270°', 270)])
            self._add_option('pages', '页面范围:', 'entry', default='全部')
            
        elif func_id == 'compress_pdf':
            self._add_option('quality', '压缩级别:', 'radio',
                            values=[('高压缩', 'high'), ('中等压缩', 'medium'), ('低压缩', 'low')])
            
        elif func_id == 'encrypt_pdf':
            self._add_option('password', '密码:', 'entry', show='*')
            self._add_option('user_password', '用户密码:', 'entry', show='*')
            
        elif func_id == 'decrypt_pdf':
            self._add_option('password', '密码:', 'entry', show='*')
            
        elif func_id == 'extract_pages':
            self._add_option('pages', '页面范围:', 'entry', default='1,3,5')
            
        elif func_id == 'delete_pages':
            self._add_option('pages', '页面范围:', 'entry', default='2,4')
            
        elif func_id == 'extract_text':
            self._add_option('pages', '页面范围:', 'entry', default='全部')
            self._add_option('output_file', '保存到文件:', 'checkbox')

    def _add_option(self, key, label, option_type, **kwargs):
        row = tk.Frame(self.options_frame, bg=C['card'])
        row.pack(fill=tk.X, pady=4)
        
        tk.Label(
            row,
            text=label,
            font=FONT['body'],
            bg=C['card'],
            fg=C['text'],
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        if option_type == 'entry':
            var = tk.StringVar(value=kwargs.get('default', ''))
            self.options[key] = var
            entry = tk.Entry(
                row,
                font=FONT['body'],
                bg=C['input_bg'],
                fg=C['text'],
                relief=tk.FLAT,
                borderwidth=1,
                textvariable=var,
                show=kwargs.get('show', None)
            )
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
        elif option_type == 'radio':
            values = kwargs.get('values', [])
            var = tk.StringVar(value=values[0][1] if values else '')
            self.options[key] = var
            
            for text, value in values:
                tk.Radiobutton(
                    row,
                    text=text,
                    variable=var,
                    value=value,
                    font=FONT['body'],
                    bg=C['card'],
                    fg=C['text'],
                    activebackground=C['card'],
                    selectcolor=C['primary_bg']
                ).pack(side=tk.LEFT, padx=(0, 12))
                
        elif option_type == 'checkbox':
            var = tk.BooleanVar(value=False)
            self.options[key] = var
            tk.Checkbutton(
                row,
                variable=var,
                font=FONT['body'],
                bg=C['card'],
                fg=C['text'],
                activebackground=C['card']
            ).pack(side=tk.LEFT)
            
        elif option_type == 'scale':
            var = tk.DoubleVar(value=kwargs.get('default', 0.5))
            self.options[key] = var
            tk.Scale(
                row,
                from_=kwargs.get('range', (0, 1))[0],
                to=kwargs.get('range', (0, 1))[1],
                orient=tk.HORIZONTAL,
                variable=var,
                bg=C['card'],
                fg=C['text'],
                troughcolor=C['border'],
                highlightthickness=0,
                length=150
            ).pack(side=tk.LEFT)

    def add_files(self):
        files = filedialog.askopenfilenames(
            title='选择 PDF 文件',
            filetypes=[('PDF 文件', '*.pdf'), ('所有文件', '*.*')]
        )
        for file in files:
            self.add_file(file)

    def add_file(self, file_path):
        if file_path not in self.file_list:
            self.file_list.append(file_path)
            self.file_listbox.insert(tk.END, os.path.basename(file_path))
            self.log(f"已添加文件: {os.path.basename(file_path)}")

    def clear_files(self):
        self.file_list.clear()
        self.file_listbox.delete(0, tk.END)
        self.log("已清空文件列表")

    def remove_selected(self):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.file_listbox.delete(index)
            removed_file = self.file_list.pop(index)
            self.log(f"已移除文件: {os.path.basename(removed_file)}")

    def select_output_dir(self):
        directory = filedialog.askdirectory(title='选择输出目录')
        if directory:
            self.output_dir = directory
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, directory)
            self.log(f"已设置输出目录: {directory}")

    def start_process(self):
        if self.is_processing:
            return
        
        if not self.current_function:
            messagebox.showwarning('提示', '请先选择要使用的功能')
            return
        
        if not self.file_list:
            messagebox.showwarning('提示', '请先添加要处理的文件')
            return
        
        if not self.output_dir:
            self.select_output_dir()
            if not self.output_dir:
                messagebox.showwarning('提示', '请选择输出目录')
                return
        
        self.is_processing = True
        self.start_button.config(state='disabled')
        self.status_indicator.set_status('正在处理...', 'working')
        self.progress_bar['value'] = 0
        
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()

    def process_files(self):
        try:
            func_id = self.current_function
            total_files = len(self.file_list)
            success_count = 0
            fail_count = 0
            
            for i, file_path in enumerate(self.file_list):
                self.root.after(0, lambda fp=file_path: self.log(f"正在处理: {os.path.basename(fp)}"))
                
                try:
                    output_name = self._get_output_name(file_path, func_id)
                    output_path = os.path.join(self.output_dir, output_name)
                    
                    self._execute_operation(func_id, file_path, output_path)
                    
                    success_count += 1
                    self.root.after(0, lambda fp=output_path: self.log(f"✓ 完成: {os.path.basename(fp)}", 'success'))
                    
                except Exception as e:
                    fail_count += 1
                    self.root.after(0, lambda err=str(e): self.log(f"✗ 失败: {err}", 'error'))
                
                self.root.after(0, lambda idx=i, tot=total_files: self.progress_bar.config(
                    value=(idx + 1) / tot * 100
                ))
            
            summary = f"处理完成！成功: {success_count}, 失败: {fail_count}"
            state = 'success' if fail_count == 0 else 'error'
            self.root.after(0, lambda: self.status_indicator.set_status(summary, state))
            self.root.after(0, lambda: self.log(summary, state))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_indicator.set_status('处理失败', 'error'))
            self.root.after(0, lambda: self.log(f"错误: {str(e)}", 'error'))
            
        finally:
            self.root.after(0, self._on_process_done)

    def _get_output_name(self, file_path, func_id):
        base_name = Path(file_path).stem
        
        name_map = {
            'pdf_to_images': f"{base_name}_images",
            'images_to_pdf': f"{base_name}_combined.pdf",
            'pdf_to_word': f"{base_name}.docx",
            'remove_watermark': f"{base_name}_clean.pdf",
            'add_watermark': f"{base_name}_watermarked.pdf",
            'merge_pdfs': "merged.pdf",
            'split_pdf': f"{base_name}_split",
            'rotate_pdf': f"{base_name}_rotated.pdf",
            'compress_pdf': f"{base_name}_compressed.pdf",
            'encrypt_pdf': f"{base_name}_encrypted.pdf",
            'decrypt_pdf': f"{base_name}_decrypted.pdf",
            'extract_pages': f"{base_name}_extracted.pdf",
            'delete_pages': f"{base_name}_modified.pdf",
            'extract_text': f"{base_name}_text.txt",
            'extract_images': f"{base_name}_images",
        }
        
        return name_map.get(func_id, f"{base_name}_output")

    def _execute_operation(self, func_id, input_path, output_path):
        opts = {k: v.get() for k, v in self.options.items()}
        
        if func_id == 'pdf_to_images':
            pages = opts.get('pages', '')
            start, end = self._parse_pages(pages)
            os.makedirs(output_path, exist_ok=True)
            self.pdf_ops.pdf_to_images(
                input_path, output_path,
                format=opts.get('format', 'png').upper(),
                dpi=int(opts.get('dpi', 150)),
                start_page=start or 1,
                end_page=end
            )
            
        elif func_id == 'images_to_pdf':
            self.pdf_ops.images_to_pdf(
                self.file_list,
                output_path,
                quality=opts.get('quality', 'high')
            )
            
        elif func_id == 'pdf_to_word':
            pages = opts.get('pages', '')
            start, end = self._parse_pages(pages)
            self.pdf_ops.pdf_to_word(
                input_path, output_path,
                start_page=start or 1,
                end_page=end
            )
            
        elif func_id == 'remove_watermark':
            self.pdf_ops.remove_watermark(
                input_path, output_path,
                watermark_type=opts.get('type', 'auto')
            )
            
        elif func_id == 'add_watermark':
            self.pdf_ops.add_watermark(
                input_path, output_path,
                text=opts.get('text', 'WATERMARK'),
                opacity=float(opts.get('opacity', 0.3)),
                position=opts.get('position', 'center')
            )
            
        elif func_id == 'merge_pdfs':
            self.pdf_ops.merge_pdfs(self.file_list, output_path)
            
        elif func_id == 'split_pdf':
            mode = opts.get('split_mode', 'ranges')
            ranges = None
            pages_per = int(opts.get('pages_per_split', 1))
            
            if mode == 'ranges':
                range_str = opts.get('ranges', '')
                ranges = self._parse_ranges(range_str)
            
            os.makedirs(output_path, exist_ok=True)
            self.pdf_ops.split_pdf(
                input_path, output_path,
                split_mode=mode,
                ranges=ranges,
                pages_per_split=pages_per
            )
            
        elif func_id == 'rotate_pdf':
            pages = opts.get('pages', '')
            page_list = self._parse_page_list(pages)
            self.pdf_ops.rotate_pdf(
                input_path, output_path,
                rotation=int(opts.get('rotation', 90)),
                pages=page_list if page_list else None
            )
            
        elif func_id == 'compress_pdf':
            self.pdf_ops.compress_pdf(
                input_path, output_path,
                quality=opts.get('quality', 'medium')
            )
            
        elif func_id == 'encrypt_pdf':
            self.pdf_ops.encrypt_pdf(
                input_path, output_path,
                password=opts.get('password', ''),
                user_password=opts.get('user_password', '')
            )
            
        elif func_id == 'decrypt_pdf':
            self.pdf_ops.decrypt_pdf(
                input_path, output_path,
                password=opts.get('password', '')
            )
            
        elif func_id == 'extract_pages':
            pages = opts.get('pages', '')
            page_list = self._parse_page_list(pages)
            self.pdf_ops.extract_pages(
                input_path, output_path,
                pages=page_list
            )
            
        elif func_id == 'delete_pages':
            pages = opts.get('pages', '')
            page_list = self._parse_page_list(pages)
            self.pdf_ops.delete_pages(
                input_path, output_path,
                pages=page_list
            )
            
        elif func_id == 'extract_text':
            pages = opts.get('pages', '')
            start, end = self._parse_pages(pages)
            to_file = opts.get('output_file', False)
            self.pdf_ops.extract_text(
                input_path,
                output_path if to_file else None,
                start_page=start or 1,
                end_page=end
            )
            
        elif func_id == 'extract_images':
            os.makedirs(output_path, exist_ok=True)
            self.pdf_ops.extract_images(input_path, output_path)

    def _parse_pages(self, pages_str):
        if not pages_str or pages_str.lower() in ['all', '全部', '']:
            return (1, None)
        
        if '-' in pages_str:
            parts = pages_str.split('-')
            return (int(parts[0]), int(parts[1]))
        
        return (int(pages_str), int(pages_str))

    def _parse_page_list(self, pages_str):
        if not pages_str or pages_str.lower() in ['all', '全部', '']:
            return None
        
        pages = []
        parts = pages_str.replace('，', ',').split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                range_parts = part.split('-')
                start = int(range_parts[0])
                end = int(range_parts[1])
                pages.extend(range(start, end + 1))
            else:
                pages.append(int(part))
        
        return pages

    def _parse_ranges(self, ranges_str):
        if not ranges_str:
            return None
        
        ranges = []
        parts = ranges_str.replace('，', ',').replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                range_parts = part.split('-')
                start = int(range_parts[0])
                end = int(range_parts[1])
                ranges.append((start, end))
        
        return ranges if ranges else None

    def _on_process_done(self):
        self.is_processing = False
        self.start_button.config(state='normal')

    def on_progress_update(self, current, total, message):
        if total > 0:
            progress = current / total * 100
            self.root.after(0, lambda: self.progress_bar.config(value=progress))
        self.root.after(0, lambda: self.progress_label.config(text=message))

    def log(self, message, tag='info'):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)
