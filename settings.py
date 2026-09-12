"""
حفظ وتحميل الإعدادات والسجل في مجلد المستخدم.

ويندوز:  %APPDATA%\ClaudeRTL\
غير كده: ~/.config/ClaudeRTL/   (عشان التطوير والاختبار)
"""

import json
import os
import tempfile
import time

APP_NAME = 'ClaudeRTL'
MAX_HISTORY = 40
MAX_ENTRY_CHARS = 40000

DEFAULTS = {
    'theme': 'dark',              # dark | light | system
    'font_family': 'plex',
    'font_size': 18,
    'line_height': 2.0,
    'measure': 72,                # أقصى عرض للسطر بوحدة ch
    'hide_tashkeel': False,
    'position_mode': 'cursor',    # cursor | remember | right
    'auto_hide_on_blur': True,
    'monitor_all_apps': False,
    'monitor_enabled': True,
    'persist_history': True,
    'pinned': False,
    'window': {'x': None, 'y': None, 'w': 540, 'h': 560},
}


def config_dir():
    if os.name == 'nt':
        base = os.environ.get('APPDATA') or os.path.expanduser('~')
    else:
        base = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')
    path = os.path.join(base, APP_NAME)
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        pass
    return path


def _path(name):
    return os.path.join(config_dir(), name)


def _read_json(path, fallback):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return fallback


def _write_json(path, data):
    """كتابة ذرّية: ملف مؤقت ثم استبدال، عشان مايحصلش تلف لو البرنامج قفل فجأة."""
    try:
        directory = os.path.dirname(path)
        fd, tmp = tempfile.mkstemp(dir=directory, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
        return True
    except OSError:
        return False


def load():
    data = _read_json(_path('settings.json'), {})
    merged = dict(DEFAULTS)
    merged['window'] = dict(DEFAULTS['window'])
    if isinstance(data, dict):
        for key, value in data.items():
            if key not in DEFAULTS:
                continue
            if key == 'window' and isinstance(value, dict):
                merged['window'].update(
                    {k: v for k, v in value.items() if k in DEFAULTS['window']}
                )
            else:
                merged[key] = value
    return merged


def save(data):
    clean = {k: v for k, v in data.items() if k in DEFAULTS}
    return _write_json(_path('settings.json'), clean)


# ─────────────────────────── السجل ───────────────────────────

def load_history():
    data = _read_json(_path('history.json'), [])
    return data if isinstance(data, list) else []


def save_history(entries):
    return _write_json(_path('history.json'), entries[:MAX_HISTORY])


def clear_history():
    try:
        os.remove(_path('history.json'))
    except OSError:
        pass


def make_entry(text):
    return {
        'id': f'{int(time.time() * 1000)}',
        'ts': time.time(),
        'text': text[:MAX_ENTRY_CHARS],
    }
