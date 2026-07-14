"""
Claude RTL Popup
popup بيظهر وقت نسخ نص عربي من Claude Desktop
"""

import webview
import threading
import time
import re
import html as html_mod
import ctypes
import ctypes.wintypes as wt
import subprocess
import os
import sys
import pystray
from PIL import Image

ARABIC_RE = re.compile(r'[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]')

HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<style>
:root {
    --accent: #D9774E;
    --bg: #1a1915;
    --card: #1a1915;
    --surface: #2b2a27;
    --ink: #ececec;
    --muted: #8b8983;
    --line: #3d3b37;
    --code-bg: #131210;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    height: 100%;
    background: var(--bg);
    font-family: "Segoe UI", "IBM Plex Sans Arabic", system-ui, sans-serif;
    color: var(--ink);
    overflow: hidden;
    border-radius: 14px;
}

/* ─── Custom title bar ─── */
.bar {
    display: flex;
    align-items: center;
    padding: 7px 12px;
    background: var(--surface);
    border-bottom: 1px solid var(--line);
    cursor: move;
    gap: 8px;
    border-radius: 14px 14px 0 0;
    user-select: none;
}
.bar .brand {
    font-size: 12px; font-weight: 700; color: var(--accent);
    display: flex; align-items: center; gap: 5px;
}
.bar .dot { width: 5px; height: 5px; border-radius: 50%; background: var(--accent); }
.bar .spacer { flex: 1; }
.bar .btn {
    background: transparent; border: none; color: var(--muted);
    font-size: 13px; width: 26px; height: 26px; border-radius: 6px;
    cursor: pointer; display: grid; place-items: center; transition: .15s;
}
.bar .btn:hover { background: var(--line); color: var(--ink); }

/* ─── Font slider ─── */
.toolbar {
    display: flex; align-items: center; gap: 8px;
    padding: 5px 12px; font-size: 11px; color: var(--muted);
    border-bottom: 1px solid var(--line);
    user-select: none;
}
.toolbar input[type="range"] { width: 80px; accent-color: var(--accent); cursor: pointer; }

/* ─── Content ─── */
.content {
    flex: 1; overflow-y: auto; padding: 14px 16px;
    font-size: 17px; line-height: 1.85;
    direction: rtl; text-align: right;
    user-select: text;
    cursor: text;
}
.content::-webkit-scrollbar { width: 6px; }
.content::-webkit-scrollbar-thumb { background: var(--line); border-radius: 6px; }

/* Text selection styling */
.content ::selection {
    background: rgba(217, 119, 78, 0.35);
    color: inherit;
}

/* ─── Empty state ─── */
.empty {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 100%; color: var(--muted); text-align: center; gap: 10px;
    user-select: none; cursor: default;
}
.empty .ic { font-size: 36px; opacity: 0.3; }
.empty .sub { font-size: 13px; }

/* ─── Fade in ─── */
.fade-in { animation: fadeIn 0.2s ease-out; }
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ─── Markdown ─── */
.content p { margin: 0.25em 0 0.5em; }
.content h1 { font-size: 1.35em; margin: 0.4em 0 0.25em; color: var(--accent); }
.content h2 { font-size: 1.2em; margin: 0.4em 0 0.25em; color: var(--accent); }
.content h3 { font-size: 1.08em; margin: 0.3em 0 0.2em; }
.content ul, .content ol { margin: 0.25em 0 0.5em; padding-inline-start: 1.3em; }
.content li { margin: 0.12em 0; }
.content blockquote {
    border-inline-start: 3px solid var(--accent);
    padding-inline-start: 11px; color: var(--muted);
    margin: 0.25em 0 0.5em;
}
.content strong { font-weight: 700; }
.content em { font-style: italic; }
.content a { color: var(--accent); text-decoration: none; }
.content hr { border: none; border-top: 1px solid var(--line); margin: .7em 0; }
.content code.inl {
    background: var(--code-bg); border: 1px solid var(--line);
    border-radius: 5px; padding: 1px 5px;
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 0.85em; direction: ltr; unicode-bidi: isolate;
}
.content pre {
    direction: ltr; unicode-bidi: isolate; text-align: left;
    background: var(--code-bg); border: 1px solid var(--line);
    border-radius: 10px; padding: 10px 12px; overflow-x: auto;
    margin: .3em 0 .6em;
}
.content pre code {
    font-family: "Cascadia Code", Consolas, monospace;
    font-size: 13px; line-height: 1.55; white-space: pre; color: var(--ink);
}

body { display: flex; flex-direction: column; }

/* ─── Resize grip ─── */
.grip {
    position: fixed; bottom: 2px; right: 2px;
    width: 14px; height: 14px; cursor: nwse-resize;
    opacity: 0.3; user-select: none;
}
.grip::after { content: '⋱'; font-size: 12px; color: var(--muted); }
</style>
</head>
<body>
    <div class="bar" id="dragBar">
        <span class="brand"><span class="dot"></span>Claude RTL</span>
        <span class="spacer"></span>
        <button class="btn" onclick="copyText()" title="نسخ">📋</button>
        <button class="btn" onclick="pywebview.api.hide_popup()" title="إغلاق (Esc)">✕</button>
    </div>
    <div class="toolbar">
        <span>الخط</span>
        <input type="range" min="13" max="28" value="17" id="fs"
               oninput="document.getElementById('content').style.fontSize=this.value+'px'">
    </div>
    <div class="content" id="content">
        <div class="empty">
            <div class="ic">📋</div>
            <div>انسخ نص عربي من Claude Desktop</div>
            <div class="sub">هيظهر هنا تلقائياً</div>
        </div>
    </div>
    <div class="grip" id="grip"></div>

<script>
    let rawText = '';
    let ignoreNextClipboard = false;

    function copyText() {
        if (!rawText) return;
        // Flag so clipboard monitor ignores this copy (it's from us)
        window.__internalCopy = true;
        navigator.clipboard.writeText(rawText).then(() => {
            setTimeout(() => { window.__internalCopy = false; }, 800);
        }).catch(() => { window.__internalCopy = false; });
    }

    function updateContent(htmlStr, plain) {
        rawText = plain || '';
        const c = document.getElementById('content');
        c.innerHTML = htmlStr;
        c.classList.remove('fade-in');
        void c.offsetWidth;
        c.classList.add('fade-in');
        c.scrollTop = 0;
    }

    // Close via Escape — works globally when window has focus
    window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            e.preventDefault();
            pywebview.api.hide_popup();
        }
    });

    // Dragging
    (function() {
        const bar = document.getElementById('dragBar');
        let dragging = false, sx, sy;
        bar.addEventListener('mousedown', (e) => {
            if (e.target.closest('.btn')) return;
            dragging = true; sx = e.screenX; sy = e.screenY;
        });
        document.addEventListener('mousemove', (e) => {
            if (!dragging) return;
            const dx = e.screenX - sx, dy = e.screenY - sy;
            sx = e.screenX; sy = e.screenY;
            pywebview.api.move_by(dx, dy);
        });
        document.addEventListener('mouseup', () => { dragging = false; });
    })();

    // Resize grip
    (function() {
        const grip = document.getElementById('grip');
        let resizing = false, sx, sy;
        grip.addEventListener('mousedown', (e) => {
            resizing = true; sx = e.screenX; sy = e.screenY;
            e.preventDefault();
        });
        document.addEventListener('mousemove', (e) => {
            if (!resizing) return;
            const dx = e.screenX - sx, dy = e.screenY - sy;
            sx = e.screenX; sy = e.screenY;
            pywebview.api.resize_by(dx, dy);
        });
        document.addEventListener('mouseup', () => { resizing = false; });
    })();
</script>
</body>
</html>'''


def has_arabic(text):
    return bool(ARABIC_RE.search(text))


def esc(text):
    return html_mod.escape(text)


def md_to_html(src):
    src = src.replace('\r\n', '\n')
    codes = []

    def save_code(m):
        codes.append(m.group(2).rstrip('\n'))
        return f'@@C{len(codes)-1}@@'
    src = re.sub(r'```(\w*)\n?([\s\S]*?)```', save_code, src)
    src = esc(src)
    src = re.sub(r'`([^`]+)`', r'<code class="inl">\1</code>', src)
    src = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', src)
    src = re.sub(r'(?<!\*)\*([^*\n]+)\*', r'<em>\1</em>', src)
    src = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', src)

    lines = src.split('\n')
    out, i, lst = [], 0, None

    def close():
        nonlocal lst
        if lst:
            out.append(f'</{lst}>')
            lst = None

    while i < len(lines):
        ln = lines[i]
        cm = re.match(r'^@@C(\d+)@@$', ln)
        if cm:
            close()
            out.append(f'<pre><code>{esc(codes[int(cm.group(1))])}</code></pre>')
            i += 1; continue
        hm = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if hm:
            close(); lvl = len(hm.group(1))
            d = 'dir="rtl"' if has_arabic(hm.group(2)) else 'dir="auto"'
            out.append(f'<h{lvl} {d}>{hm.group(2)}</h{lvl}>')
            i += 1; continue
        if re.match(r'^\s*[-*_]{3,}\s*$', ln):
            close(); out.append('<hr>'); i += 1; continue
        if re.match(r'^\s*>\s?', ln):
            close(); txt = re.sub(r'^\s*>\s?', '', ln)
            d = 'dir="rtl"' if has_arabic(txt) else 'dir="auto"'
            out.append(f'<blockquote {d}>{txt}</blockquote>')
            i += 1; continue
        ul = re.match(r'^\s*[-*+]\s+(.*)', ln)
        if ul:
            if lst != 'ul':
                close(); out.append('<ul dir="rtl">'); lst = 'ul'
            out.append(f'<li>{ul.group(1)}</li>')
            i += 1; continue
        ol = re.match(r'^\s*\d+[.)]\s+(.*)', ln)
        if ol:
            if lst != 'ol':
                close(); out.append('<ol dir="rtl">'); lst = 'ol'
            out.append(f'<li>{ol.group(1)}</li>')
            i += 1; continue
        if ln.strip() == '':
            close(); i += 1; continue
        close()
        buf = [ln]; i += 1
        while i < len(lines):
            nxt = lines[i]
            if (nxt.strip() == '' or re.match(r'^@@C\d+@@$', nxt) or
                re.match(r'^#{1,6}\s', nxt) or re.match(r'^\s*[-*+]\s', nxt) or
                re.match(r'^\s*\d+[.)]\s', nxt) or re.match(r'^\s*>\s?', nxt)):
                break
            buf.append(nxt); i += 1
        text = '<br>'.join(buf)
        d = 'dir="rtl"' if has_arabic(text) else 'dir="auto"'
        out.append(f'<p {d}>{text}</p>')
    close()
    return ''.join(out)


def escape_js(s):
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')


# ── Windows API ──
CF_UNICODETEXT = 13
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
user32.OpenClipboard.argtypes = [ctypes.c_void_p]
user32.GetClipboardData.restype = ctypes.c_void_p
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]


def get_clipboard():
    try:
        if not user32.OpenClipboard(0):
            return None
        h = user32.GetClipboardData(CF_UNICODETEXT)
        if not h:
            user32.CloseClipboard()
            return None
        p = kernel32.GlobalLock(h)
        if not p:
            user32.CloseClipboard()
            return None
        text = ctypes.wstring_at(p)
        kernel32.GlobalUnlock(h)
        user32.CloseClipboard()
        return text
    except Exception:
        try:
            user32.CloseClipboard()
        except Exception:
            pass
        return None


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


def get_cursor_pos():
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def get_screen_size():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def get_claude_pids():
    """Cache Claude Desktop PIDs (from WindowsApps)."""
    try:
        r = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             'Get-Process claude -ErrorAction SilentlyContinue | '
             'Where-Object { $_.Path -like "*WindowsApps*" } | '
             'Select-Object -ExpandProperty Id'],
            capture_output=True, text=True, creationflags=0x08000000
        )
        return {int(x.strip()) for x in r.stdout.strip().split('\n') if x.strip().isdigit()}
    except Exception:
        return set()


def is_claude_foreground(claude_pids):
    """Check if the foreground window belongs to Claude Desktop."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value in claude_pids


class Api:
    def __init__(self):
        self._window = None
        self._width = 480
        self._height = 420

    def set_window(self, w):
        self._window = w

    def hide_popup(self):
        if self._window:
            self._window.hide()

    def move_by(self, dx, dy):
        if self._window:
            self._window.move(self._window.x + dx, self._window.y + dy)

    def resize_by(self, dx, dy):
        if self._window:
            self._width = max(300, self._width + dx)
            self._height = max(200, self._height + dy)
            self._window.resize(self._width, self._height)


def force_focus(hwnd):
    user32.SetForegroundWindow(hwnd)
    user32.SetFocus(hwnd)


def find_popup_hwnd():
    """Find the pywebview popup window handle."""
    EnumWindows = user32.EnumWindows
    GetWindowTextW = user32.GetWindowTextW
    GetWindowTextLengthW = user32.GetWindowTextLengthW
    IsWindowVisible = user32.IsWindowVisible

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    result = []

    def callback(hwnd, lParam):
        length = GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            GetWindowTextW(hwnd, buf, length + 1)
            if buf.value == 'Claude RTL':
                pid = wt.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                import os
                if pid.value == os.getpid():
                    result.append(hwnd)
                    return False
        return True

    EnumWindows(WNDENUMPROC(callback), 0)
    return result[0] if result else None


def show_popup(window, api):
    mx, my = get_cursor_pos()
    sw, sh = get_screen_size()
    pw, ph = api._width, api._height

    x = mx + 15
    y = my + 15
    if x + pw > sw:
        x = mx - pw - 15
    if y + ph > sh:
        y = my - ph - 15
    x = max(10, x)
    y = max(10, y)

    window.move(x, y)
    window.show()

    hwnd = find_popup_hwnd()
    if hwnd:
        user32.SetForegroundWindow(hwnd)


def clipboard_monitor(window, api):
    last_text = ''
    claude_pids = set()
    last_pid_check = 0

    time.sleep(2)

    while True:
        try:
            now = time.time()
            # Refresh Claude PIDs every 10 seconds
            if now - last_pid_check > 10:
                claude_pids = get_claude_pids()
                last_pid_check = now

            # Only trigger if Claude Desktop is the foreground window
            if claude_pids and is_claude_foreground(claude_pids):
                text = get_clipboard()
                if text and text != last_text and has_arabic(text) and len(text.strip()) > 1:
                    last_text = text
                    content_html = md_to_html(text)
                    safe_html = escape_js(content_html)
                    safe_plain = escape_js(text)
                    window.evaluate_js(f"updateContent('{safe_html}', '{safe_plain}')")
                    show_popup(window, api)
        except Exception:
            pass
        time.sleep(0.4)


def get_icon_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'icon.ico')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')


def create_tray(api):
    icon_path = get_icon_path()
    try:
        image = Image.open(icon_path)
    except Exception:
        image = Image.new('RGB', (64, 64), color=(217, 119, 78))

    def on_quit(icon, item):
        icon.stop()
        if api._window:
            api._window.destroy()
        os._exit(0)

    menu = pystray.Menu(
        pystray.MenuItem('Claude RTL', None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('خروج / Quit', on_quit),
    )

    icon = pystray.Icon('claude_rtl', image, 'Claude RTL - شغال', menu)
    icon.run()


def main():
    api = Api()

    window = webview.create_window(
        'Claude RTL',
        html=HTML_TEMPLATE,
        width=api._width,
        height=api._height,
        min_size=(300, 200),
        resizable=True,
        on_top=True,
        frameless=True,
        easy_drag=False,
        js_api=api,
        background_color='#1a1915',
        hidden=True
    )

    api.set_window(window)

    monitor = threading.Thread(target=clipboard_monitor, args=(window, api), daemon=True)
    monitor.start()

    tray = threading.Thread(target=create_tray, args=(api,), daemon=True)
    tray.start()

    webview.start(debug=False)


if __name__ == '__main__':
    main()
