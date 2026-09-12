"""
حفظ وتحميل الإعدادات والسجل في مجلد المستخدم.

ويندوز:  %APPDATA%\ClaudeRTL\
غير كده: ~/.config/ClaudeRTL/   (عشان التطوير والاختبار)
"""

import itertools
import json
import os
import tempfile
import time

_ids = itertools.count()

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


def _coerce(value, default):
    """يرجّع القيمة بنفس نوع القيمة الافتراضية، وإلا الافتراضية نفسها.

    الملفات على الديسك ممكن تكون من إصدار أقدم أو متعدّلة بالإيد، فالنوع
    الغلط لازم يتصلّح هنا مش يوصل للواجهة.
    """
    if isinstance(default, bool):
        return bool(value)
    if isinstance(default, int):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default
    if isinstance(default, float):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    if isinstance(default, str):
        return value if isinstance(value, str) else default
    return value


def load():
    data = _read_json(_path('settings.json'), {})
    merged = dict(DEFAULTS)
    merged['window'] = dict(DEFAULTS['window'])
    if isinstance(data, dict):
        for key, value in data.items():
            if key not in DEFAULTS:
                continue
            if key == 'window':
                if isinstance(value, dict):
                    for k, v in value.items():
                        if k not in DEFAULTS['window']:
                            continue
                        merged['window'][k] = None if v is None else _coerce(v, 0)
            else:
                merged[key] = _coerce(value, DEFAULTS[key])
    return merged


def save(data):
    clean = {k: v for k, v in data.items() if k in DEFAULTS}
    return _write_json(_path('settings.json'), clean)


# ─────────────────────────── السجل ───────────────────────────

def _coerce_entry(item):
    """يحوّل أي شكل قديم لمدخلة سجل صالحة، ويرجّع None لو مافيش نص فيها.

    إصدارات أقدم كانت بتحفظ السجل كسترينجات، أو بمفاتيح تانية. من غير
    التحويل ده البرنامج بيقع وقت التحميل بدل ما يتجاهل المدخلة.
    """
    if isinstance(item, str):
        return make_entry(item) if item.strip() else None
    if not isinstance(item, dict):
        return None
    text = None
    for key in ('text', 'content', 'raw', 'body'):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            text = value
            break
    if text is None:
        return None
    entry = make_entry(text)
    if isinstance(item.get('id'), (str, int)) and not isinstance(item.get('id'), bool):
        entry['id'] = str(item['id'])
    for key in ('ts', 'time', 'timestamp'):
        value = item.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            entry['ts'] = float(value)
            break
    return entry


def load_history():
    data = _read_json(_path('history.json'), [])
    if not isinstance(data, list):
        return []
    entries, seen = [], set()
    for item in data:
        entry = _coerce_entry(item)
        if entry is None or entry['id'] in seen:
            continue
        seen.add(entry['id'])
        entries.append(entry)
    return entries[:MAX_HISTORY]


def save_history(entries):
    return _write_json(_path('history.json'), entries[:MAX_HISTORY])


def clear_history():
    try:
        os.remove(_path('history.json'))
    except OSError:
        pass


def make_entry(text):
    # العدّاد ضروري: لو اتعمل أكتر من مدخلة في نفس الملّي ثانية (وقت تحميل
    # سجل قديم مثلاً) الطابع الزمني لوحده بيدّي نفس الـid لكلهم.
    return {
        'id': f'{int(time.time() * 1000)}-{next(_ids)}',
        'ts': time.time(),
        'text': text[:MAX_ENTRY_CHARS],
    }
