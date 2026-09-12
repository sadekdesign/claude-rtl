"""
طبقة ويندوز (ctypes) — الحافظة، الشاشات، النوافذ، والاختصارات العامة.

الوحدة بتتحمّل على أي نظام؛ على غير ويندوز بترجّع قيم فاضية بدل ما تكسر
الاستيراد، عشان نقدر نتستّ باقي الكود.
"""

import ctypes
import os

IS_WINDOWS = os.name == 'nt'

CF_UNICODETEXT = 13
MONITOR_DEFAULTTONEAREST = 2
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SW_SHOWNOACTIVATE = 4
WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000

DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWCP_ROUND = 2

if IS_WINDOWS:
    from ctypes import wintypes as wt

    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    class POINT(ctypes.Structure):
        _fields_ = [('x', wt.LONG), ('y', wt.LONG)]

    class RECT(ctypes.Structure):
        _fields_ = [('left', wt.LONG), ('top', wt.LONG),
                    ('right', wt.LONG), ('bottom', wt.LONG)]

    class MONITORINFO(ctypes.Structure):
        _fields_ = [('cbSize', wt.DWORD), ('rcMonitor', RECT),
                    ('rcWork', RECT), ('dwFlags', wt.DWORD)]

    WNDENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

    user32.OpenClipboard.argtypes = [wt.HWND]
    user32.OpenClipboard.restype = wt.BOOL
    user32.CloseClipboard.restype = wt.BOOL
    user32.GetClipboardData.argtypes = [wt.UINT]
    user32.GetClipboardData.restype = wt.HANDLE
    user32.GetClipboardSequenceNumber.restype = wt.DWORD
    user32.GetForegroundWindow.restype = wt.HWND
    user32.SetForegroundWindow.argtypes = [wt.HWND]
    user32.SetFocus.argtypes = [wt.HWND]
    user32.SetFocus.restype = wt.HWND
    user32.GetWindowThreadProcessId.argtypes = [wt.HWND, ctypes.POINTER(wt.DWORD)]
    user32.GetWindowThreadProcessId.restype = wt.DWORD
    user32.GetCursorPos.argtypes = [ctypes.POINTER(POINT)]
    user32.MonitorFromPoint.argtypes = [POINT, wt.DWORD]
    user32.MonitorFromPoint.restype = ctypes.c_void_p
    user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]
    user32.EnumWindows.argtypes = [WNDENUMPROC, wt.LPARAM]
    user32.GetWindowTextW.argtypes = [wt.HWND, wt.LPWSTR, ctypes.c_int]
    user32.GetWindowTextLengthW.argtypes = [wt.HWND]
    user32.AttachThreadInput.argtypes = [wt.DWORD, wt.DWORD, wt.BOOL]
    user32.RegisterHotKey.argtypes = [wt.HWND, ctypes.c_int, wt.UINT, wt.UINT]
    user32.RegisterHotKey.restype = wt.BOOL
    user32.GetMessageW.argtypes = [ctypes.POINTER(wt.MSG), wt.HWND, wt.UINT, wt.UINT]

    kernel32.GlobalLock.argtypes = [wt.HANDLE]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [wt.HANDLE]
    kernel32.GetCurrentThreadId.restype = wt.DWORD
    kernel32.OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
    kernel32.OpenProcess.restype = wt.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wt.HANDLE, wt.DWORD, wt.LPWSTR, ctypes.POINTER(wt.DWORD)]
    kernel32.QueryFullProcessImageNameW.restype = wt.BOOL
    kernel32.CloseHandle.argtypes = [wt.HANDLE]


# ─────────────────────────── الحافظة ───────────────────────────

def clipboard_sequence():
    """رقم بيتغيّر مع كل تعديل على الحافظة — أرخص بكتير من فتحها كل مرة."""
    if not IS_WINDOWS:
        return 0
    return user32.GetClipboardSequenceNumber()


def get_clipboard_text():
    if not IS_WINDOWS:
        return None
    opened = False
    try:
        # الحافظة ممكن تكون مقفولة من برنامج تاني للحظة
        for _ in range(3):
            if user32.OpenClipboard(None):
                opened = True
                break
        if not opened:
            return None
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return None
        ptr = kernel32.GlobalLock(handle)
        if not ptr:
            return None
        try:
            return ctypes.wstring_at(ptr)
        finally:
            kernel32.GlobalUnlock(handle)
    except Exception:
        return None
    finally:
        if opened:
            try:
                user32.CloseClipboard()
            except Exception:
                pass


# ─────────────────────────── المؤشر والشاشات ───────────────────────────

def cursor_pos():
    if not IS_WINDOWS:
        return 0, 0
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def work_area_at(x, y):
    """مساحة العمل للشاشة اللي تحت النقطة دي (من غير شريط المهام)."""
    if not IS_WINDOWS:
        return 0, 0, 1920, 1080
    try:
        monitor = user32.MonitorFromPoint(POINT(x, y), MONITOR_DEFAULTTONEAREST)
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if monitor and user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            r = info.rcWork
            return r.left, r.top, r.right, r.bottom
    except Exception:
        pass
    return 0, 0, user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


# ─────────────────────────── العمليات والنوافذ ───────────────────────────

_name_cache = {}


def _process_name(pid):
    if pid in _name_cache:
        return _name_cache[pid]
    name = ''
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if handle:
        try:
            size = wt.DWORD(260)
            buf = ctypes.create_unicode_buffer(size.value)
            if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                name = os.path.basename(buf.value).lower()
        finally:
            kernel32.CloseHandle(handle)
    if len(_name_cache) > 256:
        _name_cache.clear()
    _name_cache[pid] = name
    return name


def foreground_process_name():
    """اسم ملف البرنامج صاحب النافذة النشطة، بدون تشغيل أي بروسيس خارجي."""
    if not IS_WINDOWS:
        return ''
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ''
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if not pid.value:
        return ''
    return _process_name(pid.value)


def find_window(title, pid=None):
    """يدوّر على نافذة بعنوان معيّن تخص البروسيس ده."""
    if not IS_WINDOWS:
        return None
    pid = os.getpid() if pid is None else pid
    found = []

    def callback(hwnd, _lparam):
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if buf.value != title:
            return True
        wpid = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value == pid:
            found.append(hwnd)
            return False
        return True

    try:
        user32.EnumWindows(WNDENUMPROC(callback), 0)
    except Exception:
        return None
    return found[0] if found else None


def force_foreground(hwnd):
    """ويندوز بيرفض SetForegroundWindow من بروسيس مش نشط — الحيلة دي بتعدّيها."""
    if not IS_WINDOWS or not hwnd:
        return
    try:
        current = kernel32.GetCurrentThreadId()
        fore = user32.GetForegroundWindow()
        other = 0
        if fore:
            pid = wt.DWORD()
            other = user32.GetWindowThreadProcessId(fore, ctypes.byref(pid))
        attached = bool(other and other != current
                        and user32.AttachThreadInput(current, other, True))
        user32.SetForegroundWindow(hwnd)
        user32.SetFocus(hwnd)
        if attached:
            user32.AttachThreadInput(current, other, False)
    except Exception:
        pass


def round_corners(hwnd):
    """حواف دائرية على ويندوز 11 (بيتجاهلها الإصدارات الأقدم بدون ضرر)."""
    if not IS_WINDOWS or not hwnd:
        return
    try:
        dwmapi = ctypes.WinDLL('dwmapi')
        pref = ctypes.c_int(DWMWCP_ROUND)
        dwmapi.DwmSetWindowAttribute(
            wt.HWND(hwnd), DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(pref), ctypes.sizeof(pref))
    except Exception:
        pass


# ─────────────────────────── الاختصارات العامة ───────────────────────────

def hotkey_loop(bindings, on_hotkey):
    """
    يسجّل اختصارات عامة ويفضل يسمع لها.

    bindings: قاموس {id: (modifiers, virtual_key)}
    لازم يشتغل في ثريد مستقل — RegisterHotKey مربوط بالثريد اللي سجّلها.
    """
    if not IS_WINDOWS:
        return
    registered = []
    for hotkey_id, (mods, vk) in bindings.items():
        if user32.RegisterHotKey(None, hotkey_id, mods | MOD_NOREPEAT, vk):
            registered.append(hotkey_id)
    if not registered:
        return
    msg = wt.MSG()
    while True:
        result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
        if result in (0, -1):
            break
        if msg.message == WM_HOTKEY:
            try:
                on_hotkey(int(msg.wParam))
            except Exception:
                pass


def foreground_hwnd():
    if not IS_WINDOWS:
        return None
    return user32.GetForegroundWindow()
