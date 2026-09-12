"""اختبارات محرك الماركداون — بتشتغل على أي نظام: python3 tests/test_mdrender.py"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mdrender  # noqa: E402

CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


def contains(html, *needles):
    for n in needles:
        assert n in html, f'ناقص: {n!r}\n---\n{html}'


@case('كشف العربي والاتجاه')
def _():
    assert mdrender.has_arabic('مرحبا')
    assert not mdrender.has_arabic('hello 123')
    contains(mdrender.render('مرحبا بالعالم'), '<p dir="rtl">', 'مرحبا بالعالم')
    contains(mdrender.render('hello world'), '<p dir="auto">')


@case('العناوين')
def _():
    contains(mdrender.render('## عنوان'), '<h2 dir="rtl">عنوان</h2>')
    contains(mdrender.render('###### ستة'), '<h6 dir="rtl">ستة</h6>')


@case('التوكيد والشطب')
def _():
    html = mdrender.render('نص **غامق** و *مائل* و ~~مشطوب~~')
    contains(html, '<strong>غامق</strong>', '<em>مائل</em>', '<del>مشطوب</del>')


@case('الكود السطري محمي من التنسيق')
def _():
    html = mdrender.render('جرّب `a ** b ** c` كده')
    contains(html, '<code class="inl" dir="ltr">a ** b ** c</code>')
    assert '<strong>' not in html


@case('بلوك كود بلغة وزر نسخ')
def _():
    html = mdrender.render('```python\nprint("hi")\n```')
    contains(html, 'class="codeblock"', '<span class="lang">python</span>',
             'class="ccopy"', 'print(&quot;hi&quot;)')


@case('الماركداون جوه الكود مايتفسّرش')
def _():
    html = mdrender.render('```\n# مش عنوان\n- مش ليستة\n```')
    assert '<h1' not in html and '<ul' not in html


@case('قوائم متداخلة')
def _():
    html = mdrender.render('- أ\n  - أ١\n  - أ٢\n- ب')
    assert html.count('<ul') == 2, html
    contains(html, '<li>أ', '<li>أ١</li>', '<li>ب</li>')


@case('قائمة مرقّمة')
def _():
    html = mdrender.render('1. واحد\n2. اتنين')
    contains(html, '<ol dir="rtl">', '<li>واحد</li>', '<li>اتنين</li>')


@case('قائمة مهام')
def _():
    html = mdrender.render('- [x] خلصت\n- [ ] لسه')
    contains(html, 'type="checkbox" disabled checked', 'خلصت', 'لسه')


@case('جدول بمحاذاة')
def _():
    html = mdrender.render('| الاسم | العدد |\n|:---|---:|\n| أحمد | 5 |')
    contains(html, '<table dir="rtl">', '<th style="text-align:left">الاسم</th>',
             '<th style="text-align:right">العدد</th>', '<td style="text-align:left">أحمد</td>')


@case('اقتباس متعدد الأسطر')
def _():
    html = mdrender.render('> سطر أول\n> سطر تاني')
    contains(html, '<blockquote dir="rtl">', 'سطر أول')


@case('الروابط')
def _():
    contains(mdrender.render('[كلاود](https://claude.ai)'),
             '<a href="https://claude.ai" data-ext="1">كلاود</a>')
    contains(mdrender.render('شوف https://example.com/x كده'),
             '<a href="https://example.com/x" data-ext="1">')


@case('رابط جافاسكربت بيتحيّد')
def _():
    html = mdrender.render('[اضغط](javascript:alert(1))')
    assert 'javascript:' not in html, html
    contains(html, 'href="#"')


@case('الهروب من HTML')
def _():
    html = mdrender.render('<script>alert(1)</script>')
    assert '<script>' not in html
    contains(html, '&lt;script&gt;')


@case('فاصل أفقي')
def _():
    contains(mdrender.render('---'), '<hr>')
    assert '<hr>' not in mdrender.render('- عنصر')


@case('إزالة التشكيل')
def _():
    assert mdrender.strip_tashkeel('مُحَمَّدٌ') == 'محمد'


@case('السطر الليّن بيتجمّع، والصريح بيكسر')
def _():
    soft = mdrender.render('سطر أول\nسطر تاني')
    contains(soft, '<p dir="rtl">سطر أول سطر تاني</p>')
    assert '<br>' not in soft, soft
    hard = mdrender.render('سطر أول  \nسطر تاني')
    contains(hard, 'سطر أول<br>سطر تاني')
    slash = mdrender.render('سطر أول\\\nسطر تاني')
    contains(slash, 'سطر أول<br>سطر تاني')


@case('نص مختلط طويل')
def _():
    html = mdrender.render(
        '# التقرير\n\n'
        'ده **ملخص** فيه `code` ورابط [هنا](https://x.co).\n'
        'سطر تاني في نفس الفقرة.  \n'
        'وده بكسر صريح.\n\n'
        '- نقطة\n  1. فرعية\n\n'
        '| أ | ب |\n|---|---|\n| 1 | 2 |\n\n'
        '```js\nconst x = 1;\n```\n\n'
        '> اقتباس\n'
    )
    contains(html, '<h1 dir="rtl">', '<br>', '<ol', '<table', 'codeblock', '<blockquote')


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
