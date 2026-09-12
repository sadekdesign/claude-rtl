"""اختبارات حفظ/تحميل الإعدادات والسجل: python3 tests/test_settings.py"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


def fresh_store():
    """يرجّع موديول settings مربوط بمجلد مؤقت فاضي."""
    import importlib
    import settings as store
    importlib.reload(store)
    tmp = tempfile.mkdtemp()
    store.config_dir = lambda: tmp
    return store, tmp


def write(tmp, name, data):
    with open(os.path.join(tmp, name), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


@case('السجل القديم كسترينجات بيتحوّل مايكسرش')
def _():
    # ده بالظبط اللي وقّع البرنامج: نسخة أقدم حفظت السجل كسترينجات
    store, tmp = fresh_store()
    write(tmp, 'history.json', ['نص أول', 'نص تاني'])
    entries = store.load_history()
    assert len(entries) == 2, entries
    for e in entries:
        assert set(e) == {'id', 'ts', 'text'}, e
        assert isinstance(e['id'], str) and isinstance(e['ts'], float)
    assert entries[0]['text'] == 'نص أول'


@case('مفاتيح قديمة مختلفة بتتقرا')
def _():
    store, tmp = fresh_store()
    write(tmp, 'history.json', [
        {'content': 'بمفتاح content', 'timestamp': 1700000000},
        {'body': 'بمفتاح body'},
    ])
    entries = store.load_history()
    assert [e['text'] for e in entries] == ['بمفتاح content', 'بمفتاح body'], entries
    assert entries[0]['ts'] == 1700000000.0


@case('المدخلات الفاسدة بتتشال بدل ما توقّع')
def _():
    store, tmp = fresh_store()
    write(tmp, 'history.json', [None, 42, [], {}, {'text': '   '}, 'سليم'])
    entries = store.load_history()
    assert [e['text'] for e in entries] == ['سليم'], entries


@case('ملف سجل مش ليستة بيرجّع فاضي')
def _():
    store, tmp = fresh_store()
    write(tmp, 'history.json', {'oops': True})
    assert store.load_history() == []


@case('المعرّفات فريدة حتى لو اتعملوا مع بعض')
def _():
    store, tmp = fresh_store()
    write(tmp, 'history.json', [f'نص {i}' for i in range(20)])
    ids = [e['id'] for e in store.load_history()]
    assert len(set(ids)) == len(ids) == 20, ids


@case('السجل بيتقصّ على الحد الأقصى')
def _():
    store, tmp = fresh_store()
    write(tmp, 'history.json', [f'نص {i}' for i in range(store.MAX_HISTORY + 15)])
    assert len(store.load_history()) == store.MAX_HISTORY


@case('الأنواع الغلط في الإعدادات بتترد لنوعها')
def _():
    store, tmp = fresh_store()
    write(tmp, 'settings.json', {
        'font_size': '22',            # سترينج بدل رقم
        'line_height': '1.8',
        'hide_tashkeel': 1,           # رقم بدل بوليان
        'theme': 99,                  # رقم بدل سترينج
        'measure': 'مش رقم',
    })
    cfg = store.load()
    assert cfg['font_size'] == 22 and isinstance(cfg['font_size'], int)
    assert cfg['line_height'] == 1.8
    assert cfg['hide_tashkeel'] is True
    assert cfg['theme'] == store.DEFAULTS['theme']     # رجع للافتراضي
    assert cfg['measure'] == store.DEFAULTS['measure']


@case('مقاس النافذة بيقبل null وبيرفض الهري')
def _():
    store, tmp = fresh_store()
    write(tmp, 'settings.json', {'window': {'x': None, 'y': '40', 'w': 700, 'h': 'خمسمية'}})
    win = store.load()['window']
    assert win['x'] is None and win['y'] == 40 and win['w'] == 700
    assert win['h'] == 0 or win['h'] == store.DEFAULTS['window']['h'], win


@case('ملف إعدادات بايظ بيرجّع الافتراضيات')
def _():
    store, tmp = fresh_store()
    with open(os.path.join(tmp, 'settings.json'), 'w', encoding='utf-8') as f:
        f.write('{ ليس JSON على الإطلاق')
    assert store.load()['font_size'] == store.DEFAULTS['font_size']


@case('الحفظ والتحميل رايح جاي')
def _():
    store, tmp = fresh_store()
    store.save({'theme': 'light', 'font_size': 26, 'مفتاح غريب': 1})
    cfg = store.load()
    assert cfg['theme'] == 'light' and cfg['font_size'] == 26
    assert 'مفتاح غريب' not in cfg
    entries = [store.make_entry('واحد'), store.make_entry('اتنين')]
    store.save_history(entries)
    assert [e['text'] for e in store.load_history()] == ['واحد', 'اتنين']


def main():
    failed = 0
    for name, fn in CASES:
        try:
            fn()
            print(f'  \033[32mOK\033[0m   {name}')
        except AssertionError as exc:
            failed += 1
            print(f'  \033[31mFAIL\033[0m {name}\n       {exc}')
    print(f'\n{len(CASES) - failed}/{len(CASES)} نجحت')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
