"""
Claude RTL — قارئ عربي منبثق.

بيراقب الحافظة، ولما تنسخ نص عربي بيظهر popup بيعرضه مظبوط من اليمين
لليسار بتنسيق ماركداون مقروء، مع سجل وإعدادات بتتحفظ.
"""

import json
import os
import re
import sys
import threading
import time
import webbrowser

import webview

import mdrender
import settings as cfg_store
import ui
import winapi

APP_TITLE = 'Claude RTL'
SOURCE_APPS = {'claude.exe'}           # البرامج اللي بنراقب النسخ منها افتراضياً
POLL_INTERVAL = 0.25
MIN_W, MIN_H = 340, 260

HOTKEY_SHOW = 1
HOTKEY_TOGGLE = 2
VK_A, VK_D = 0x41, 0x44


def _relative_time(ts):
    delta = max(0, int(time.time() - ts))
    if delta < 60:
        return 'الآن'
    if delta < 3600:
        return f'من {delta // 60} دقيقة'
    if delta < 86400:
        return f'من {delta // 3600} ساعة'
    return time.strftime('%Y/%m/%d', time.localtime(ts))


def _preview(text, limit=110):
    flat = re.sub(r'\s+', ' ', text).strip()
    return flat[:limit] + ('…' if len(flat) > limit else '')


def _word_count(text):
    return len(text.split())


class Api:
    """السطح اللي الواجهة بتناديه. الميثودز العامة بس هي اللي بتتعرّض لـ JS."""

    def __init__(self, app):
        self._app = app

    def hide_popup(self):
        self._app.hide()

    def move_by(self, dx, dy):
        self._app.move_by(int(dx), int(dy))

    def resize_by(self, dw, dh):
        self._app.resize_by(int(dw), int(dh))

    def geometry_changed(self):
        self._app.remember_geometry()

    def save_settings(self, data):
        self._app.update_settings(data or {})

    def set_pinned(self, value):
        self._app.set_pinned(bool(value))

    def open_url(self, url):
        if isinstance(url, str) and re.match(r'^(https?|mailto):', url, re.I):
            try:
                webbrowser.open(url)
            except Exception:
                pass

    def load_entry(self, entry_id):
        return self._app.entry_payload(str(entry_id))

    def clear_history(self):
        self._app.clear_history()
        return True


class ClaudeRTL:
    def __init__(self):
        self.cfg = cfg_store.load()
        self.history = cfg_store.load_history() if self.cfg['persist_history'] else []
        self.window = None
        self.tray = None
        self._hwnd = None
        self._visible = False
        self._last_text = ''
        self._own_name = os.path.basename(sys.executable).lower()

        win = self.cfg['window']
        self._w = max(MIN_W, int(win.get('w') or 540))
        self._h = max(MIN_H, int(win.get('h') or 560))
        self._x = win.get('x')
        self._y = win.get('y')

    # ─────────────── الجسر مع الواجهة ───────────────

    def _js(self, func, *args):
        if not self.window:
            return
        payload = ', '.join(json.dumps(a, ensure_ascii=True) for a in args)
        try:
            self.window.evaluate_js(f'{func}({payload})')
        except Exception:
            pass

    def on_loaded(self):
        # أي استثناء هنا بيطلع جوه حلقة أحداث pywebview ويوقف الإقلاع،
        # فالأأمن إن الواجهة تفتح حتى لو السجل المحفوظ بايظ.
        try:
            self._js('init', self.cfg)
            self.push_history()
        except Exception:
            self.history = []
            self._js('setHistory', [])

    # ─────────────── الإعدادات ───────────────

    def update_settings(self, data):
        for key, value in data.items():
            if key in cfg_store.DEFAULTS and key != 'window':
                self.cfg[key] = value
        self.cfg['window'] = {'x': self._x, 'y': self._y, 'w': self._w, 'h': self._h}
        cfg_store.save(self.cfg)
        if not self.cfg['persist_history']:
            cfg_store.clear_history()

    def remember_geometry(self):
        self.cfg['window'] = {'x': self._x, 'y': self._y, 'w': self._w, 'h': self._h}
        cfg_store.save(self.cfg)

    def set_pinned(self, value):
        # التثبيت بيوقّف الإخفاء التلقائي بس — النافذة فوق الكل في الحالتين
        self.cfg['pinned'] = value
        cfg_store.save(self.cfg)

    # ─────────────── السجل ───────────────

    def push_history(self):
        self._js('setHistory', [
            {
                'id': e['id'],
                'preview': _preview(e['text']),
                'when': _relative_time(e['ts']),
                'words': _word_count(e['text']),
            }
            for e in self.history
        ])

    def entry_payload(self, entry_id):
        for entry in self.history:
            if entry['id'] == entry_id:
                return {'html': mdrender.render(entry['text']), 'plain': entry['text']}
        return None

    def clear_history(self):
        self.history = []
        cfg_store.clear_history()
        self.push_history()

    def _record(self, text):
        self.history = [e for e in self.history if e['text'] != text]
        self.history.insert(0, cfg_store.make_entry(text))
        del self.history[cfg_store.MAX_HISTORY:]
        if self.cfg['persist_history']:
            cfg_store.save_history(self.history)
        self.push_history()

    # ─────────────── العرض ───────────────

    def _place(self):
        mode = self.cfg['position_mode']
        w, h = self._w, self._h

        if mode == 'remember' and self._x is not None and self._y is not None:
            x, y = int(self._x), int(self._y)
            left, top, right, bottom = winapi.work_area_at(x, y)
        else:
            mx, my = winapi.cursor_pos()
            left, top, right, bottom = winapi.work_area_at(mx, my)
            if mode == 'right':
                x = right - w - 24
                y = top + max(0, (bottom - top - h) // 2)
            else:
                x, y = mx + 18, my + 18
                if x + w > right:
                    x = mx - w - 18
                if y + h > bottom:
                    y = my - h - 18

        x = max(left, min(x, right - w))
        y = max(top, min(y, bottom - h))
        self._x, self._y = x, y
        try:
            self.window.move(x, y)
        except Exception:
            pass

    def show(self, focus=True):
        if not self.window:
            return
        self._place()
        try:
            self.window.show()
        except Exception:
            return
        self._visible = True
        if self._hwnd is None:
            self._hwnd = winapi.find_window(APP_TITLE)
            winapi.round_corners(self._hwnd)
        if focus:
            winapi.force_foreground(self._hwnd)

    def hide(self):
        self._visible = False
        self.remember_geometry()
        try:
            self.window.hide()
        except Exception:
            pass

    def toggle(self):
        if self._visible:
            self.hide()
        elif self._last_text:
            self.show()
        elif self.history:
            self.display(self.history[0]['text'], record=False)

    def display(self, text, record=True):
        self._last_text = text
        if record:
            self._record(text)
        self._js('updateContent', mdrender.render(text), text, True)
        self.show()

    def move_by(self, dx, dy):
        if self._x is None or self._y is None:
            return
        self._x += dx
        self._y += dy
        try:
            self.window.move(self._x, self._y)
        except Exception:
            pass

    def resize_by(self, dw, dh):
        new_w = max(MIN_W, self._w + dw)
        new_h = max(MIN_H, self._h + dh)
        shift = new_w - self._w       # المقبض في الركن الشمال، فالحافة دي بتتحرك
        self._w, self._h = new_w, new_h
        try:
            self.window.resize(self._w, self._h)
            if shift and self._x is not None:
                self._x -= shift
                self.window.move(self._x, self._y)
        except Exception:
            pass

    # ─────────────── مراقبة الحافظة ───────────────

    def _source_allowed(self):
        if self._hwnd and winapi.foreground_hwnd() == self._hwnd:
            return False            # إحنا اللي نسخنا
        name = winapi.foreground_process_name()
        if not name or name == self._own_name:
            return False
        if self.cfg['monitor_all_apps']:
            return True
        return name in SOURCE_APPS

    def monitor(self):
        time.sleep(1.5)
        last_seq = winapi.clipboard_sequence()
        while True:
            try:
                seq = winapi.clipboard_sequence()
                if seq != last_seq:
                    last_seq = seq
                    if self.cfg['monitor_enabled'] and self._source_allowed():
                        text = winapi.get_clipboard_text()
                        if (text and text != self._last_text
                                and len(text.strip()) > 1
                                and mdrender.has_arabic(text)):
                            self.display(text)
            except Exception:
                pass
            time.sleep(POLL_INTERVAL)

    # ─────────────── الاختصارات العامة ───────────────

    def set_monitoring(self, enabled):
        self.cfg['monitor_enabled'] = bool(enabled)
        cfg_store.save(self.cfg)
        self._js('setMonitoring', self.cfg['monitor_enabled'])
        if self.tray:
            self.tray.update_menu()

    def on_hotkey(self, hotkey_id):
        if hotkey_id == HOTKEY_SHOW:
            self.toggle()
        elif hotkey_id == HOTKEY_TOGGLE:
            self.set_monitoring(not self.cfg['monitor_enabled'])

    def hotkeys(self):
        winapi.hotkey_loop(
            {
                HOTKEY_SHOW: (winapi.MOD_CONTROL | winapi.MOD_SHIFT, VK_A),
                HOTKEY_TOGGLE: (winapi.MOD_CONTROL | winapi.MOD_SHIFT, VK_D),
            },
            self.on_hotkey,
        )

    # ─────────────── أيقونة شريط المهام ───────────────

    def run_tray(self):
        import pystray
        from PIL import Image

        try:
            image = Image.open(icon_path())
        except Exception:
            image = Image.new('RGB', (64, 64), (217, 119, 87))

        def quit_app(icon, _item):
            self.remember_geometry()
            icon.stop()
            try:
                self.window.destroy()
            except Exception:
                pass
            os._exit(0)

        menu = pystray.Menu(
            pystray.MenuItem('إظهار آخر نص', lambda: self.toggle(), default=True),
            pystray.MenuItem(
                'مراقبة الحافظة',
                lambda: self.set_monitoring(not self.cfg['monitor_enabled']),
                checked=lambda _i: self.cfg['monitor_enabled'],
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('الإعدادات', lambda: (self.show(), self._js('openSettings'))),
            pystray.MenuItem('خروج', quit_app),
        )
        self.tray = pystray.Icon('claude_rtl', image, f'{APP_TITLE} — شغال', menu)
        self.tray.run()

    # ─────────────── التشغيل ───────────────

    def run(self):
        self.window = webview.create_window(
            APP_TITLE,
            html=ui.HTML,
            width=self._w,
            height=self._h,
            min_size=(MIN_W, MIN_H),
            resizable=True,
            on_top=True,
            frameless=True,
            easy_drag=False,
            js_api=Api(self),
            background_color='#1B1B19',
            hidden=True,
        )
        self.window.events.loaded += self.on_loaded

        for target in (self.monitor, self.hotkeys, self.run_tray):
            threading.Thread(target=target, daemon=True).start()

        webview.start(debug=False)


def icon_path():
    base = (os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
            else os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, 'icon.ico')


if __name__ == '__main__':
    ClaudeRTL().run()
